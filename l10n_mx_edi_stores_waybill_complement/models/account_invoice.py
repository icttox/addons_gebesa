# Copyright 2022, Cesar Barron
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import requests
import simplejson as json
from odoo.exceptions import UserError
from odoo import models, fields, api, exceptions, _


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    income_invoice_id = fields.Many2one(
        'account.invoice',
        string='Income invoice',
    )

    unit_id = fields.Many2one(
        'fleet.vehicle',
        string='Unit',)

    trailer1_id = fields.Many2one(
        'fleet.vehicle',
        string='Trailer1')

    dolly_id = fields.Many2one(
        'fleet.vehicle',
        string='Dolly',
        domain=[('fleet_type', '=', 'dolly')])

    trailer2_id = fields.Many2one(
        'fleet.vehicle',
        string='Trailer2',
        domain=[('fleet_type', '=', 'trailer')])

    driver_id = fields.Many2one(
        'hr.employee',
        string='Driver',
        domain=[('driver', '=', True)])

    driver_two_id = fields.Many2one(
        'hr.employee',
        string='Driver 2',
        domain=[('driver', '=', True)])

    departure_address_id = fields.Many2one(
        'res.partner',
        string='Departure address',
    )

    date_departure = fields.Datetime(
        string='Start Real'
    )

    date_deliver = fields.Datetime(
        string='End Real'
    )

    insurance_policy = fields.Char(
        string="Insurance number"
    )

    insurance_supplier_id = fields.Many2one(
        'res.partner',
        string='Insurance Supplier'
    )

    environmental_insurance_policy = fields.Char(
        string="Insurance environmental number"
    )

    environmental_insurance_supplier_id = fields.Many2one(
        'res.partner',
        string='Environmental Insurance Supplier'
    )

    @api.multi
    def _get_invline_weights(self, field, product_id=False):
        suma = 0
        for inv in self:
            transportable = inv.mapped('invoice_line_ids')
            if product_id:
                transportable = transportable.filtered(
                    lambda x: x.product_id.id == product_id)
            for tras in transportable:
                suma += tras.product_id.weight * tras.quantity
            return round(suma, 4)

    @api.multi
    def _l10n_mx_edi_create_cfdi_values(self):
        """Create the values to fill the CFDI template with external trade.
        """
        values = super()._l10n_mx_edi_create_cfdi_values()

        if values['document_type'] == 'traslado':
            values['invoice_line_ids'] = self.income_invoice_id.invoice_line_ids

        if not self.unit_id and not self.driver_id:
            return values

        values['distancias'] = self._store_waybill_distance()

        values['transp_internac'] = 'No'
        values['entrada_salida_merc'] = False
        values['via_entrada_salida'] = False
        values['pais_origen_destino'] = False

        values['cant_trans'] = True
        # # if (len(self.mapped('travel_ids').mapped('delivery_ids')) > 1 or len(self.mapped('travel_ids').mapped('transportable_line_ids').mapped('transportable_id')) > 1):
        # if len(self.mapped('travel_ids').mapped('transportable_line_ids').mapped('transportable_id')) > 1:
        #     values['cant_trans'] = True

        return values

    @api.multi
    def _store_waybill_distance(self):
        url = 'https://maps.googleapis.com/maps/api/distancematrix/json'
        dic_distance = {
            'total': 0.00
        }
        for inv in self:
            origins = (
                str(inv.departure_address_id.place_id.latitude) + ',' + str(
                    inv.departure_address_id.place_id.longitude))
            destinations = ''
            new_origin = self.env['tms.place']
            # for delivery in travel.delivery_ids:
            destinations += (
                str(inv.partner_shipping_id.place_id.latitude) + ',' + str(
                    inv.partner_shipping_id.place_id.longitude) + '|')
            if new_origin:
                origins += '|' + str(new_origin.latitude) + ',' + str(
                    new_origin.longitude)
            new_origin = inv.partner_shipping_id.place_id
            params = {
                'origins': origins,
                'destinations': destinations[:-1],
                'mode': 'driving',
                'language': self.env.lang,
                'sensor': 'false',
                'key': 'AIzaSyCKBWo-QHHefkWfPZaPjAJT9HDtpY307KI',
            }
            try:
                result = json.loads(requests.get(url, params=params).content)
            except Exception:
                raise exceptions.UserError(
                    "Google Maps is not available.")
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
            if not inv.unit_id or not inv.driver_id:
                continue

            if not inv.company_id.stc_type_permit or not inv.company_id.sct_reg:
                raise UserError(_("The company must have a permit type and permit number."))

            if inv.trailer1_id and not inv.trailer1_id.sub_type_rem:
                raise UserError(_("Trailers must have a trailer subtype."))

            if inv.trailer2_id and not inv.trailer2_id.sub_type_rem:
                raise UserError(_("Trailers must have a trailer subtype."))

            if not inv.unit_id.conf_vehicle:
                raise UserError(_("The unit must have a transport configuration."))

            if not inv.partner_shipping_id:
                raise UserError(_("The invoice must have at a delivery address."))

            if not inv.departure_address_id:
                raise UserError(_("The invoice must have departure address."))

            if not inv.income_invoice_id.invoice_line_ids:
                raise UserError(_("The invoice must have at least one line."))

            if not inv.departure_address_id.street_name or not inv.departure_address_id.l10n_mx_edi_locality_id:
                raise UserError(_("Departure address location and street is missing."))

            if not inv.departure_address_id.state_id or not inv.departure_address_id.country_id:
                raise UserError(_("Departure address country and state is missing."))

            if not inv.departure_address_id.city_id:
                raise UserError(_("Departure address city is missing."))

            if not inv.departure_address_id.zip:
                raise UserError(_("Departure address postal code is missing."))

            if not inv.departure_address_id.place_id:
                raise UserError(_("Departure address place is missing."))

            if not inv.partner_shipping_id.place_id:
                raise UserError(_("The shipping address must have its own location."))

            if not inv.partner_shipping_id.street_name or not inv.partner_shipping_id.l10n_mx_edi_locality_id:
                raise UserError(_("The locaty and street of the delivery company %s is missing." % inv.partner_shipping_id.name))

            if not inv.partner_shipping_id.state_id or not inv.partner_shipping_id.country_id:
                raise UserError(_("The country and state of the delivery company %s is missing." % inv.partner_shipping_id.name))

            if not inv.partner_shipping_id.city_id:
                raise UserError(_("The city of the delivery company %s is missing." % inv.partner_shipping_id.name))

            if not inv.partner_shipping_id.zip:
                raise UserError(_("The postal code of the delivery company %s is missing." % inv.partner_shipping_id.name))

            for line in inv.income_invoice_id.invoice_line_ids:
                # Add to the product
                if not line.product_id.products_services_id:
                    raise UserError(_("All the products must have a Waybill classification."))

                if not line.product_id.weight > 0.0:
                    raise UserError(_("The product must have a loading weight."))

                if not line.quantity > 0.0:
                    raise UserError(_("The travel must have a loading quantity."))

        return result
