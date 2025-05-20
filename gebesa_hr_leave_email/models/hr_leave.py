# Copyright 2022, Marco Esquivel
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import re
from datetime import datetime
from odoo import models, api
from odoo.tools import email_split
from odoo.exceptions import UserError


class HrLeaveAlias(models.Model):
    _inherit = 'hr.leave'

    @api.model
    def message_new(self, msg_dict, custom_values=None):
        try:
            if custom_values is None:
                custom_values = {}

            email_address = email_split(msg_dict.get('email_from', False))[0]

            if not email_address:
                raise UserError("No se puede crear la ausencia porque no se encontro el correo del empleado")
            employee = self.env['hr.employee'].sudo().search([
                '|',
                ('work_email', 'ilike', email_address),
                ('user_id.email', 'ilike', email_address)
            ], limit=1)
            if not employee:
                raise UserError("No se puede crear la ausencia porque no se encontro el empleado")

            tipo_match = re.search(r'Tipo: (\w+)', msg_dict.get('body', ''))
            tipo = tipo_match.group(1) if tipo_match else None

            if not tipo:
                raise UserError("No se puede crear la ausencia porque no se proporcionó bien el tipo de ausencia")

            tipo_ausencia = self.env['hr.leave.type'].sudo().search([
                ('company_id', '=', employee.company_id.id),
                ('code', '=', tipo)
            ], limit=1)

            if not tipo_ausencia:
                raise UserError("No se puede crear la ausencia porque no se encontró el tipo de ausencia")

            msg_body = msg_dict.get('body', '')
            cleaner = re.compile('<.*?>')
            clean_msg_body = re.sub(cleaner, '', msg_body)
            date_list = re.findall(r'\d{2}/\d{2}/\d{4}', clean_msg_body)

            if len(date_list) != 2:
                raise UserError("No se puede crear la ausencia porque no se proporcionaron bien las fechas.")

            date_from = datetime.strptime(date_list[0], '%d/%m/%Y')
            date_to = datetime.strptime(date_list[1], '%d/%m/%Y')

            if date_to < date_from:
                raise UserError("No se puede crear la ausencia porque la fecha final de la ausencia es menor a la de inicio.")

            str_date_from = date_from.strftime('%Y-%m-%d')
            str_date_to = date_to.strftime('%Y-%m-%d')

            date_to = date_to.replace(hour=23)

            custom_values.update({
                'employee_id': employee.id,
                'holiday_status_id': tipo_ausencia.id,
                'request_date_from': str_date_from,
                'request_date_to': str_date_to,
                'date_from': date_from,
                'date_to': date_to,
                'holiday_type': 'employee',
            })
            res = super(HrLeaveAlias, self).message_new(msg_dict, custom_values)
            res._onchange_request_parameters()
            return res

        except UserError as us_er:
            error_message = "No se puedo crear la ausencia debido a un error: <li>%s</li>" % us_er.name
            email_to = email_split(msg_dict.get('to', False))[0]

            mail_obj = self.env['mail.mail']
            mail = mail_obj.create({
                'subject': 'Error al procesar solicitud de ausencia',
                'email_from': email_to,
                'email_to': email_address,
                'headers': "{'Return-Path': u'%s'}" % email_to,
                'body_html': '<p>%s</p>' % error_message,
                'auto_delete': True,
                'message_type': 'comment',
            })
            mail.send()

        return self.env['hr.leave']
