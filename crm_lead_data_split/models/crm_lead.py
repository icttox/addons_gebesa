# -*- coding: utf-8 -*-
# © 2017 Aldo Nerio
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
import traceback
from odoo import api, models, _
from odoo import tools
from odoo.tools import html2plaintext

_logger = logging.getLogger(__name__)


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    @api.model
    def create(self, vals):
        res = super().create(vals)
        # if not res.contact_name:
        custom_values = {}
        self.substring_message(custom_values)
        return res

    @api.multi
    def substring_message(self, msg, custom_values=None):
        _logger.error(
            _('Entrando al substring_message'))
        mail_obj = self.env['mail.message']
        for lead in self:
            _logger.error(
                _('lead in self'))
            mail_var = mail_obj.search([('model', '=', 'crm.lead'),
                                        ('res_id', '=', lead.id),
                                        ('message_type', '=', 'email')])
            custom_values = {}
            if mail_var:
                _logger.error(
                    _('si hay mail'))
                custom_values, msg = self.prepare_substring_message(mail_var, custom_values)
                lead.write(custom_values)
        return True

    def prepare_substring_message(self, msg, custom_values=None):

        def parse_description(description):
            fields = [
                'correo', 'email', 'nombre', 'empresa', 'apellido',
                'telefono', 'ciudad', 'estado',
                'comentarios', 'fuente', u'cómo nos conoce']
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

        subject = msg.subject
        subject = subject.lower()
        _logger.error(
            _(subject))

        if 'new submission' in subject:
            if custom_values is None:
                custom_values = {}

            # message = msg.body.replace('\r\n', ' ')
            message = msg.body.replace('<br>', ' ')
            desc = html2plaintext(message) if message else ''

            desc = desc.replace('*\n\n\n', ': ')
            desc = desc.replace('*', '')
            # desc = desc.replace('\r\n', ' ')

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
            apellido = False
            _logger.error(
                _('Antes de los if'))

            if _dict.get('email'):
                email_from = _dict.get('email')

                _logger.error(
                    _(email_from))

            if _dict.get('nombre'):
                contact_name = _dict.get('nombre').title()

                _logger.error(
                    _(contact_name))

            if _dict.get('apellido'):
                apellido = _dict.get('apellido').title()

                _logger.error(
                    _(apellido))

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

            if _dict.get(u'cómo nos conoce'):
                referred = _dict.get(u'cómo nos conoce')
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

            if apellido:
                apellido = apellido.rstrip()
                _logger.error(
                    _('apellido: ' + apellido))

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
                'email_from': email_from.replace(' [1]', ''),
                'contact_name': contact_name + ' ' + apellido,
                'partner_name': partner_name,
                'phone': phone,
                'city': city,
                'referred': referred,
                'description': description,
                'partner_id': partner_id[0] if partner_id else False,
            }
            _logger.error(
                _(vals))

            custom_values.update(vals)
            _logger.error(
                _(custom_values))
        return custom_values, msg

    @api.model
    def force_autofill(self):

        pending = self.env['crm.lead'].search(
            [('contact_name', '=', False)], limit=500)

        for lead in pending:
            # dife = order.amount_total - order.total_nste
            # if abs(dife) > 0.6000:
            #     continue

            try:
                lead.substring_message()
                self.env.cr.commit()
            except Exception:
                error = tools.ustr(traceback.format_exc())
                _logger.error(
                    _('Error al llenar los datos: %s' % lead.name))
                _logger.error(
                    _('Error es: %s' % error))
                continue

            # except Exception:
            #     _logger.error(
            #         _('Error al validar el pedido %s' % order.name))
            #     continue
        return True
