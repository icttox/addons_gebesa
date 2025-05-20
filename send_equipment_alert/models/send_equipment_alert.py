# -*- coding: utf-8 -*-
# © <2018> <Aldo Nerio>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime
from odoo import fields, models, api


class send_alert_equipment(models.Model):
    _inherit = 'maintenance.equipment'

    @api.model
    def send_email_equipment_alert_m(self):

        eq = self.search([
            ('active', '=', True)])
        table = ''
        for x in eq:
            limit_date = x.fecha_vencimiento
            ubicacion = x.location
            note = x.note
            name = x.name
            num_s = x.serial_no
            if limit_date:
                dd = datetime.today()
                days = fields.Datetime.from_string(limit_date) - dd
                days = days.days
                if days <= 7:
                    remp_date = limit_date
                    remp_rep = ''
                    if not x.location:
                        ubicacion = '----------'
                    if not x.name:
                        remp_rep = '----------'
                    else:
                        remp_rep = name
                    if not num_s:
                        num_s = '-----------'
                    table += """
                        <tr><td style="border-bottom: 1px solid silver;">%s</td>
                            <td style="border-bottom: 1px solid silver;">%s</td>
                            <td style="border-bottom: 1px solid silver;">%s</td>
                            <td style="border-bottom: 1px solid silver;">%s</td>
                            <td align="right" style="border-bottom: 1px solid silver;">
                            %s</td></tr>
                    """ % (num_s, remp_rep, note, remp_date, ubicacion)
        mail_obj = self.env['mail.mail']
        body_mail = u"""
                    <div summary="o_mail_notification" style="padding:0px; width:700px;
                     margin:0 auto; background: #FFFFFF repeat top /100%%; color:#77777
                     7">
                        <table cellspacing="0" cellpadding="0" style="width:700px;
                        border-collapse:collapse; background:inherit; color:inherit">
                            <tbody><tr>
                                <td valign="center" width="270" style="padding:5px 10px
                                 5px 5px;font-size: 18px">
                                    <p>La garantia de los siguientes equipos esta proxima a vencer</p>
                                </td>
                                <td valign="center" align="right" width="270"
                                style="padding:5px 15px 5px 10px; font-size: 12px;">
                                    <p>
                                    <strong>Sent by</strong>
                                    <a href="http://erp.portalgebesa.com" style="text-
                                    decoration:none; color: #a24689;">
                                        <strong>%s</strong>
                                    </a>
                                    <strong>using</strong>
                                    <a href="https://www.odoo.com" style="text-
                                    decoration:none; color: #a24689;"><strong>Odoo
                                    </strong></a>
                                    </p>
                                </td>
                            </tr>
                        </tbody></table>
                    </div>
                    <div style="padding:0px; width:700px; margin:0 auto; background:
                    #FFFFFF repeat top /100%%; color:#777777">
                        <table cellspacing="0" cellpadding="0" style="vertical-align:
                        top; padding:0px; border-collapse:collapse; background:inherit;
                         color:inherit">
                            <tbody><tr>
                                <td valign="top" style="width:700px; padding:5px 10px
                                5px 5px; ">
                                    <div>
                                        <hr width="100%%" style="background-color:
                                        rgb(204,204,204);border:medium none;clear:both;
                                        display:block;font-size:0px;min-height:1px;
                                        line-height:0;margin:15px auto;padding:0">
                                    </div>
                                </td>
                            </tr></tbody>
                        </table>
                    </div>
                    <div style="padding:0px; width:700px; margin:0 auto; background:
                    #FFFFFF repeat top /100%%;color:#777777">
                        <table style="border-collapse:collapse; margin: 0 auto; width:
                        700px; background:inherit; color:inherit">
                            <tbody><tr>
                               <th width="15%%" style="padding:5px 10px 5px 5px;font-
                                size: 14px; border-bottom: 2px solid silver;"><strong>
                                Num Serie</strong></th>
                                <th width="16%%" style="padding:5px 10px 5px 5px;font-
                                size: 14px; border-bottom: 2px solid silver;"><strong>
                                Nombre</strong></th>
                                <th width="15%%" style="padding:5px 10px 5px 5px;font-
                                size: 14px; border-bottom: 2px solid silver;"><strong>
                                Descripcion</strong></th>
                                <th width="15%%" style="padding:5px 10px 5px 5px;font-
                                size: 14px; border-bottom: 2px solid silver;"><strong>
                                Fecha Vencimiento</strong></th>
                                <th width="15%%" style="padding:5px 10px 5px 5px;font-
                                size: 14px; border-bottom: 2px solid silver;"><strong>
                                Ubicacion</strong></th>
                            </tr>
                            %s
                            </tbody>
                        </table>
                    </div>
                  """ % (self.env.user.company_id.name, table)
        mail = mail_obj.create({
            'subject': 'Garantia proxima a vencer',
            'email_to': 'soportetecnico@gebesa.com',
            'headers': "{'Return-Path': u'odoo@gebesa.com'}",
            'body_html': body_mail,
            'auto_delete': True,
            'message_type': 'comment',
        })
        mail.send()
