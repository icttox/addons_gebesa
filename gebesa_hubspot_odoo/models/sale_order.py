# Copyright 2024, Marco Esquivel
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import re
from odoo import models, api, fields
from odoo.tools import email_split
from odoo.exceptions import UserError


class SaleOrderAlias(models.Model):
    _inherit = 'sale.order'

    folio_hubspot = fields.Char(
        string='Folio HubSpot',
    )

    @api.model
    def message_new(self, msg_dict, custom_values=None):
        try:
            if custom_values is None:
                custom_values = {}

            mail_obj = self.env['mail.mail']
            email_address = email_split(msg_dict.get('email_from', False))[0]
            email_to = email_split(msg_dict.get('to', False))[0]

            partner = re.search(r'partner: (.+?)(?:\r\n|$)', msg_dict.get('body', ''), re.UNICODE)
            if not partner:
                raise UserError("No se puede crear el pedido porque la etiquta de cliente no esta bien escrita")
            partner_hubspot = partner.group(1)

            company = re.search(r'company: (\w+)', msg_dict.get('body', ''))
            if not company:
                raise UserError("No se puede crear el pedido porque la etiquta de la compañia no esta bien escrita")
            company_hubspot = company.group(1)

            company_id = self.env['res.company'].sudo().search([
                ('vat', '=', company_hubspot)], limit=1)
            if not company_id:
                raise UserError("No se puede crear el pedido porque no se encontro la compañia")

            partner_id = self.env['res.partner'].sudo().search([
                ('partner_hubspot', '=', partner_hubspot),
                ('active', '=', True),
                ('customer', '=', True),
                ('company_id', '=', company_id.id)], limit=1)
            if not partner_id:
                name = re.search(r'name: (\w+)', msg_dict.get('body', ''))
                name_hubspot = name.group(1) if name else partner_hubspot

                partner_id = self.env['res.partner'].sudo().create({
                    'name': name_hubspot,
                    'customer': True,
                    'active': True,
                    'partner_hubspot': partner_hubspot,
                    'company_id': company_id.id,
                })

            sequence_id = self.env['ir.sequence'].sudo().search([
                ('code', '=', 'sale.order'),
                ('company_id', '=', company_id.id)], limit=1)

            if sequence_id:
                next_number = sequence_id.next_by_id()

            hubspot = re.search(r'hubspot_id: (\w+)', msg_dict.get('body', ''))
            hubspot_id = hubspot.group(1) if hubspot else False

            custom_values.update({
                'name': next_number,
                'partner_id': partner_id.id,
                'company_id': company_id.id,
                'folio_hubspot': hubspot_id,
            })
            res = super(SaleOrderAlias, self).message_new(msg_dict, custom_values)
            res.onchange_partner_id()

            template_id = mail_obj.create({
                'name': 'Notificación de orden de venta creada',
                'subject': 'Nueva orden de venta creada: %s' % res.name,
                'email_from': email_to,
                'email_to': email_address,
                'body_html': """
                    <p>Se ha creado una nueva orden de venta con los siguientes detalles:</p>
                    <ul>
                        <li>Folio de SO: %s </li>
                        <li>Folio de HubSpot: %s </li>
                        <li>Compañia: %s </li>
                        <li>Cliente: %s </li>
                        </ul>
                """ % (res.name, res.folio_hubspot, res.company_id.name, res.partner_id.name)
            })
            template_id.send()
            return res

        except UserError as us_er:
            error_message = "No se puedo crear el registro debido a un error: <li>%s</li>" % us_er.name
            mail = mail_obj.create({
                'subject': 'Error al crear un presupuesto de venta',
                'email_from': email_to,
                'email_to': email_address,
                'headers': "{'Return-Path': u'%s'}" % email_to,
                'body_html': '<p>%s</p>' % error_message,
                'auto_delete': True,
                'message_type': 'comment',
            })
            mail.send()

        return self.env['sale.order']
