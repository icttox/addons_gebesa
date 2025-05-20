# -*- coding: utf-8 -*-
# © 2017 Aldo Nerio
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from odoo import api, models, _
from odoo.tools import html2plaintext

_logger = logging.getLogger(__name__)


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    def _prepare_message_new_custom_values(self, msg,
                                           custom_values=None):
        def parse_description(description):
            fields = [
                'correo', 'nombre', 'empresa',
                'telefono', 'ciudad', 'estado',
                'comentarios', 'fuente', 'url']
            _dict = {}
            description = description.lower()
            for line in description.split('\n'):
                for field in fields:
                    if field in line:
                        split_line = line.split(':')
                        if len(split_line) > 1:
                            _dict[field] = line.split(':')[1].strip()
            return _dict

        _logger.error(
            _('Entrando al segundo metodo'))

        subject = msg.get('subject', '')
        subject = subject.lower()
        _logger.error(
            _(subject))

        if 'new submission' in subject:
            if custom_values is None:
                custom_values = {}

            desc = html2plaintext(msg.get('body')) if msg.get('body') \
                else ''

            desc = desc.replace('*\n\n\n', ': ')
            desc = desc.replace('*', '')

            _logger.error(
                _(desc))

            _dict = parse_description(desc)

            contact_name = False
            email_from = False
            partner_name = False
            phone = False
            city = False
            referred = False
            description = False

            _logger.error(
                _('Antes de los if'))

            if _dict.get('correo'):
                email_from = _dict.get('correo')

                _logger.error(
                    _(email_from))

            if _dict.get('nombre'):
                contact_name = _dict.get('nombre').title()

                _logger.error(
                    _(contact_name))

            if _dict.get('empresa'):
                partner_name = _dict.get('empresa').title()

                _logger.error(
                    _(partner_name))

            if _dict.get('telefono'):
                phone = _dict.get('telefono')
                _logger.error(
                    _(phone))

            if _dict.get('ciudad'):
                city = _dict.get('ciudad').title()
                _logger.error(
                    _(city))

            if _dict.get('url'):
                referred = _dict.get('url')
                _logger.error(
                    _(referred))

            if _dict.get('comentarios'):
                description = _dict.get('comentarios').title()
                _logger.error(
                    _(description))

            # Search for an existing partner:
            if contact_name and email_from:
                partner_id = self.env['res.partner'].search([
                    '|', ('name', '=', contact_name),
                    ('email', '=', email_from)], limit=1)
            elif contact_name and not email_from:
                partner_id = self.env['res.partner'].search([
                    ('name', '=', contact_name)], limit=1)
            elif email_from and not contact_name:
                partner_id = self.env['res.partner'].search([
                    ('email', '=', email_from)], limit=1)
            else:
                partner_id = False

            if email_from:
                email_from = email_from.rstrip()
                _logger.error(
                    _('email_from: ' + email_from))

            if contact_name:
                contact_name = contact_name.rstrip()
                _logger.error(
                    _('contact_name: ' + contact_name))

            if partner_name:
                partner_name = partner_name.rstrip()
                _logger.error(
                    _('partner_name: ' + partner_name))

            if phone:
                phone = phone.rstrip()
                _logger.error(
                    _('phone: ' + phone))

            if city:
                city = city.rstrip()
                _logger.error(
                    _('city: ' + city))

            if referred:
                referred = referred.rstrip()
                _logger.error(
                    _('referred: ' + referred))

            if description:
                description = description.rstrip()
                _logger.error(
                    _('description: ' + description))

            # description = desc
            vals = {
                'email_from': email_from,
                'contact_name': contact_name,
                'partner_name': partner_name,
                'phone': phone,
                'city': city,
                'referred': referred,
                'description': description,
                'partner_id': partner_id[0] if partner_id else False,
            }
            _logger.error(
                _(vals))

            # self.contact_name = contact_name
            # self.partner_name = partner_name
            # self.phone = phone
            # self.city = city
            # self.referred = referred
            # self.description = description
            msg['from'] = _dict.get('correo')
            custom_values.update(vals)
            _logger.error(
                _(custom_values))
        return custom_values, msg

    @api.model
    def message_new(self, msg, custom_values=None):
        _logger.error(
            _('Entrando al metodo con valores write'))

        rec_id = super().message_new(msg=msg, custom_values=custom_values)

        _logger.error(_('Pruebas dos'))

        _logger.error(msg)
        _logger.error(custom_values)

        body = msg.get('body')

        _logger.error(body)

        model = self._name
        if model == 'crm.lead':
            custom_values = {}
            # lead_obj = self.env[model]
            custom_values, msg = self._prepare_message_new_custom_values(
                msg, custom_values)
            if custom_values:
                _logger.error(
                    _('Escribir:'))
                _logger.error(
                    _(custom_values))

                # for rec in self:
                #     _logger.error(
                #         _('RecID: ' + rec.id))
                #     rec.contact_name = custom_values.get('contact_name')
                #     rec.partner_name = custom_values.get('partner_name')
                #     rec.phone = custom_values.get('phone')
                #     rec.city = custom_values.get('city')
                #     rec.referred = custom_values.get('referred')
                #     rec.description = custom_values.get('description')

                self.write(custom_values)
        return rec_id
