# -*- coding: utf-8 -*-

import requests
import logging
import simplejson as json
import googlemaps
import uuid
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from odoo.exceptions import UserError
from odoo import models, fields, api, exceptions, _

_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    l10n_mx_edi_waybill_complement = fields.Boolean(
        string='Need Waybill Complement',
        compute='_compute_need_waybill_complement',
    )

    l10n_mx_edi_skip_waybill = fields.Boolean(
        'Skip Waybill?',
        compute='_compute_skip_waybill',
        inverse='_inverse_skip_waybill', store=True,
        help='If this field is active, the CFDI that generate this invoice '
        'will to include the complement "Skip Waybill".')

    l10n_mx_edi_waybill_id_ccp = fields.Char(
        string='Id CCP',
    )

    @api.depends('partner_id')
    def _compute_skip_waybill(self):
        """Assign the Need Skip Waybill? value how in the partner"""
        for record in self.filtered(lambda i: i.type == 'out_invoice'):
            record.l10n_mx_edi_skip_waybill = record.partner_id.l10n_mx_edi_skip_waybill

    def _inverse_skip_waybill(self):
        return True

    @api.depends('travel_ids')
    def _compute_need_waybill_complement(self):
        for inv in self:
            if inv.travel_ids:
                inv.l10n_mx_edi_waybill_complement = True
            else:
                inv.l10n_mx_edi_waybill_complement = False

    @api.model
    def l10n_mx_edi_get_complement_waybill_version(self):
        '''Returns the cfdi version to generate the CFDI.
        '''
        version = self.env['ir.config_parameter'].sudo().get_param(
            'l10n_mx_edi_cfdi_complement_waybill_version', '2.0')
        return version

    @api.multi
    def _get_transportable_weights(self, field, transportable_id=False):
        suma = 0
        for inv in self:
            transportable = inv.mapped('travel_ids').mapped(
                'transportable_line_ids')
            if transportable_id:
                transportable = transportable.filtered(
                    lambda x: x.transportable_id.id == transportable_id)
            for tras in transportable:
                suma += tras[field] * tras.quantity
            return round(suma, 4)

    @api.multi
    def _get_id_ccp_waybill(self):
        new_id = True
        while new_id:
            id_ccp = str(uuid.uuid4())
            id_ccp = 'CCC' + id_ccp[3:]
            inv = self.search([('l10n_mx_edi_waybill_id_ccp', '=', id_ccp)])
            if not inv:
                new_id = False
        return id_ccp

    @api.multi
    def _l10n_mx_edi_create_cfdi_values(self):
        """Create the values to fill the CFDI template with external trade.
        """
        values = super()._l10n_mx_edi_create_cfdi_values()
        if not self.l10n_mx_edi_waybill_complement:
            return values

        if self.l10n_mx_edi_skip_waybill:
            return values

        complement_version = self.l10n_mx_edi_get_complement_waybill_version()
        values['complement_waybill_version'] = complement_version

        if complement_version == '3.0':
            self.l10n_mx_edi_waybill_id_ccp = self._get_id_ccp_waybill()
            values['id_ccp'] = self.l10n_mx_edi_waybill_id_ccp

        if all(deliv.distance_previous_point > 0 for deliv in self.mapped(
                'travel_ids').mapped('delivery_ids')):
            values['distancias'] = self._l10n_mx_edi_waybill_manual_distance()
        else:
            values['distancias'] = self._l10n_mx_edi_waybill_distance()
        # values['distancias'] = self._l10n_mx_edi_waybill_distance_with_gmaps()

        values['transp_internac'] = 'No'
        values['entrada_salida_merc'] = False
        values['via_entrada_salida'] = False
        values['pais_origen_destino'] = False

        if any(travel.international for travel in self.travel_ids):
            values['transp_internac'] = 'Sí'
            if self.travel_ids[0].in_out == 'out':
                values['entrada_salida_merc'] = 'Salida'
                values['pais_origen_destino'] = 'MEX'
            else:
                values['entrada_salida_merc'] = 'Entrada'
                values['pais_origen_destino'] = self.travel_ids[0].departure_address_id.country_id.fiscal_code
            values['via_entrada_salida'] = self.travel_ids[
                0].via_in_out_id.code

        values['cant_trans'] = False
        # if (len(self.mapped('travel_ids').mapped('delivery_ids')) > 1 or len(self.mapped('travel_ids').mapped('transportable_line_ids').mapped('transportable_id')) > 1):
        if len(self.mapped('travel_ids').mapped('transportable_line_ids').mapped('transportable_id')) > 1:
            values['cant_trans'] = True

        return values

    @api.multi
    def _l10n_mx_edi_render_replace_cfdi(self, template, values):
        cfdi = super()._l10n_mx_edi_render_replace_cfdi(template, values)
        if 'complement_waybill_version' in values:
            if values['complement_waybill_version'] == '2.0':
                cfdi = cfdi.replace(
                    b'<cartaporte20:CartaPorte xmlns:cartaporte20="http://www.sat.gob.mx/CartaPorte20" xsi:schemaLocation="http://www.sat.gob.mx/CartaPorte20 http://www.sat.gob.mx/sitio_internet/cfd/CartaPorte/CartaPorte20.xsd"',
                    b'<cartaporte20:CartaPorte')
            elif values['complement_waybill_version'] == '3.0':
                cfdi = cfdi.replace(
                    b'<cartaporte30:CartaPorte xmlns:cartaporte30="http://www.sat.gob.mx/CartaPorte30" xsi:schemaLocation="http://www.sat.gob.mx/CartaPorte30 http://www.sat.gob.mx/sitio_internet/cfd/CartaPorte/CartaPorte30.xsd"',
                    b'<cartaporte30:CartaPorte')
                cfdi = cfdi.replace(
                    b'<cartaporte31:CartaPorte xmlns:cartaporte31="http://www.sat.gob.mx/CartaPorte31" xsi:schemaLocation="http://www.sat.gob.mx/CartaPorte31 http://www.sat.gob.mx/sitio_internet/cfd/CartaPorte/CartaPorte31.xsd"',
                    b'<cartaporte31:CartaPorte')

        return cfdi

    @api.multi
    def _l10n_mx_edi_waybill_manual_distance(self):
        dic_distance = {
            'total': 0.00
        }
        num = 0
        for travel in self.travel_ids:
            for delivery in travel.delivery_ids:
                dic_distance[str(num)] = round(
                    delivery.distance_previous_point, 3)
                dic_distance['total'] += round(
                    delivery.distance_previous_point, 3)
                num = num + 1
        dic_distance['total'] = round(dic_distance['total'], 3)
        return dic_distance

    @api.multi
    def _l10n_mx_edi_waybill_distance_with_gmaps(self):
        api_key = 'AIzaSyCKBWo-QHHefkWfPZaPjAJT9HDtpY307KI'
        dic_distance = {
            'total': 0.00
        }
        gmaps = googlemaps.Client(key=api_key)

        for travel in self.travel_ids:
            origins = (
                str(travel.departure_address_id.place_id.latitude) + ',' + str(
                    travel.departure_address_id.place_id.longitude))
            destinations = ''
            new_origin = self.env['tms.place']
            for delivery in travel.delivery_ids:
                destinations += (
                    str(delivery.partner_id.place_id.latitude) + ',' + str(
                        delivery.partner_id.place_id.longitude) + '|')
                if new_origin:
                    origins += '|' + str(new_origin.latitude) + ',' + str(
                        new_origin.longitude)
                new_origin = delivery.partner_id.place_id
            try:
                result = json.loads(gmaps.distance_matrix(origins, destinations[:-1], mode='driving'))
                _logger.error(
                    _('Result Gmaps library distance: %s' % result))
            except Exception as exc:
                raise exceptions.UserError(_(
                    "Error trying reaching Google Maps (library): %s") % str(exc))
            if result['status'] == 'OK':
                num = 0
                for row in result['rows']:
                    if row['elements'][num]['status'] == 'ZERO_RESULTS':
                        raise exceptions.UserError(
                            "No se encontro una ruta valida para una entrega. Por favor de revisar los lugares de sus entregas o del punto de salida")
                    distance = (
                        row['elements'][num]['distance']
                           ['value'] / 1000.0)
                    dic_distance[str(num)] = round(distance, 3)
                    dic_distance['total'] += round(distance, 3)
                    num = num + 1
            else:
                errmsj = result['error_message']
                message_body = "<b>%s:</b> %s" % (
                    "El servicio de googlemaps regresó el siguiente error: ", errmsj)
                raise exceptions.UserError(message_body)
            if dic_distance['total'] == 0.00:
                raise exceptions.UserError(
                    "La distancia total del viaje debe ser mayor a 0. Por favor de revisar los lugares de sus entregas o del punto de salida")
        dic_distance['total'] = round(dic_distance['total'], 3)
        return dic_distance

    @api.multi
    def _l10n_mx_edi_waybill_distance(self):
        url = 'https://maps.googleapis.com/maps/api/distancematrix/json'
        dic_distance = {
            'total': 0.00
        }
        for travel in self.travel_ids:
            origins = (
                str(travel.departure_address_id.place_id.latitude) + ',' + str(
                    travel.departure_address_id.place_id.longitude))
            destinations = ''
            new_origin = self.env['tms.place']
            for delivery in travel.delivery_ids:
                destinations += (
                    str(delivery.partner_id.place_id.latitude) + ',' + str(
                        delivery.partner_id.place_id.longitude) + '|')
                if new_origin:
                    origins += '|' + str(new_origin.latitude) + ',' + str(
                        new_origin.longitude)
                new_origin = delivery.partner_id.place_id
            params = {
                'origins': origins,
                'destinations': destinations[:-1],
                'mode': 'driving',
                'language': self.env.lang,
                'sensor': 'false',
                'key': 'AIzaSyCKBWo-QHHefkWfPZaPjAJT9HDtpY307KI',
            }
            _logger.error(
                _('Gmaps distance params: %s' % params))
            try:
                sess = requests.Session()
                retry = Retry(connect=3, backoff_factor=1)
                adapter = HTTPAdapter(max_retries=retry)
                sess.mount('http://', adapter)
                sess.mount('https://', adapter)
                result = json.loads(sess.get(url, timeout=(3, 4), params=params).content)
                _logger.error(
                    _('Result Gmaps distance: %s' % result))
            except Exception as exc:
                raise exceptions.UserError(_(
                    "Error trying reaching out Google Maps: %s") % str(exc))
            if result['status'] == 'OK':
                num = 0
                for row in result['rows']:
                    if row['elements'][num]['status'] == 'ZERO_RESULTS':
                        raise exceptions.UserError(
                            "No se encontro una ruta valida para una entrega. Por favor de revisar los lugares de sus entregas o del punto de salida")
                    distance = (
                        row['elements'][num]['distance']
                           ['value'] / 1000.0)
                    dic_distance[str(num)] = round(distance, 3)
                    dic_distance['total'] += round(distance, 3)
                    num = num + 1
            else:
                errmsj = result['error_message']
                message_body = "<b>%s:</b> %s" % (
                    "El servicio de googlemaps regresó el siguiente error: ", errmsj)
                raise exceptions.UserError(message_body)
            if dic_distance['total'] == 0.00:
                raise exceptions.UserError(
                    "La distancia total del viaje debe ser mayor a 0. Por favor de revisar los lugares de sus entregas o del punto de salida")
        dic_distance['total'] = round(dic_distance['total'], 3)
        return dic_distance

    @api.multi
    def _perform_l10n_mx_validations(self):
        result = super()._perform_l10n_mx_validations()
        for inv in self:
            if not inv.travel_ids:
                continue
            if inv.l10n_mx_edi_skip_waybill:
                continue
            for travel in inv.travel_ids:
                if not inv.company_id.stc_type_permit or not inv.company_id.sct_reg:
                    raise UserError(_("The company must have a permit type and permit number."))

                if not travel.trailer1_id.sub_type_rem:
                    raise UserError(_("Trailers must have a trailer subtype."))

                if travel.trailer2_id and not travel.trailer2_id.sub_type_rem:
                    raise UserError(_("Trailers must have a trailer subtype."))

                if not travel.unit_id.conf_vehicle:
                    raise UserError(_("The unit must have a transport configuration."))

                if not travel.delivery_ids:
                    raise UserError(_("The travel must have at least one delivery."))

                if not travel.departure_address_id:
                    raise UserError(_("The travel must have departure address."))

                if not travel.transportable_line_ids:
                    raise UserError(_("The travel must have transportable line."))

                if not travel.departure_address_id.street_name or not travel.departure_address_id.l10n_mx_edi_locality_id:
                    raise UserError(_("Departure address location and street is missing."))

                if not travel.departure_address_id.state_id or not travel.departure_address_id.country_id:
                    raise UserError(_("Departure address country and state is missing."))

                if not travel.departure_address_id.city_id:
                    raise UserError(_("Departure address city is missing."))

                if not travel.departure_address_id.zip:
                    raise UserError(_("Departure address postal code is missing."))

                if not travel.departure_address_id.place_id:
                    raise UserError(_("Departure address place is missing."))

                entrega = travel.mapped('delivery_ids')
                place = entrega.mapped('partner_id').mapped('place_id')
                if len(entrega) != len(place):
                    raise UserError(_("Each delivery must have its own location, and you cannot repeat a delivery."))

                for trans_line in travel.transportable_line_ids:
                    if not trans_line.transportable_id.products_services_id:
                        raise UserError(_("Must have the transportable have a type of product or service."))

                    if not trans_line.delivery_id:
                        raise UserError(_("The travel must have a loading address."))

                    if not trans_line.weight > 0.0:
                        raise UserError(_("The travel must have a loading weight."))

                    if not trans_line.quantity > 0.0:
                        raise UserError(_("The travel must have a loading quantity."))

                for delivery in travel.delivery_ids:
                    if not delivery.partner_id.place_id:
                        raise UserError(_("The place of the delivery company %s is missing." % delivery.partner_id.name))

                    if not delivery.partner_id.street_name or not delivery.partner_id.l10n_mx_edi_locality_id:
                        raise UserError(_("The locaty and street of the delivery company %s is missing." % delivery.partner_id.name))

                    if not delivery.partner_id.state_id or not delivery.partner_id.country_id:
                        raise UserError(_("The country and state of the delivery company %s is missing." % delivery.partner_id.name))

                    if not delivery.partner_id.city_id:
                        raise UserError(_("The city of the delivery company %s is missing." % delivery.partner_id.name))

                    if not delivery.partner_id.zip:
                        raise UserError(_("The postal code of the delivery company %s is missing." % delivery.partner_id.name))

        return result
