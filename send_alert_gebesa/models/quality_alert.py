# Copyright 2022, Samuel Barron
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models
from datetime import timedelta


class QualityAlert(models.Model):
    _inherit = 'quality.alert'

    def get_html_body_send_email_alert_queality(self, table=None, date=None):
        body_mail = u"""
            <div summary="o_mail_notification" style="padding:0px; width:90%%;
                margin:0 auto; background: #FFFFFF repeat top /100%%; color:#777777">
                <table cellspacing="0" cellpadding="0" style="width:100%%;
                border-collapse:collapse;">
                    <tbody><tr>
                        <td valign="center" width="270" style="padding:5px 10px
                         5px 5px;font-size: 17px; font-family:'Arial';">
                            <b>Alertas de calidad del dia %s</b>
                        </td>
                        <td valign="center" align="right" width="270"
                        style="padding:5px 15px 5px 10px; font-family:'Arial'; font-size: 12px;">
                            <p>
                            <strong>Sent by</strong>
                            <a href="http://erp.portalgebesa.com" style="text-
                            decoration:none; color: #a24689; font-family:'Arial';">
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
            <div style="padding:0px; width:900px; margin:0 auto; background:
            #FFFFFF repeat top /100%%; color:#777777">
                <table cellspacing="0" cellpadding="0" style="vertical-align:
                top; padding:0px; border-collapse:collapse; background:inherit;
                 color:inherit">
                    <tbody><tr>
                        <td valign="top" style="width:70%%; padding:5px 10px
                        5px 5px; ">
                            <div>
                                <hr width="900px" style="background-color:
                                rgb(204,204,204);border:medium none;clear:both;
                                display:block;font-size:0px;min-height:1px;
                                line-height:0;margin:15px auto;padding:0">
                            </div>
                        </td>
                    </tr></tbody>
                </table>
            </div>
            <div style="padding:0px; width:100%%; margin:0 auto; background:
            #FFFFFF repeat top /100%%; color:#fff">
                <table style="border-collapse:collapse; margin: 0 auto; width:
                90%%; background:inherit; color:inherit">
                    <tbody>
                    <tr style="font-size: 15px; font-family:'Arial';">
                        <th style="padding:5px 10px 5px 5px; border-bottom: 10px solid silver; background-color: #a24689;">
                            <strong>Alerta</strong>
                        </th>
                        <th style="padding:5px 10px 5px 5px; border-bottom: 10px solid silver; background-color: #a24689;">
                            <strong>Titulo</strong>
                        </th>
                        <th style="padding:5px 10px 5px 5px; border-bottom: 10px solid silver; background-color: #a24689;">
                            <strong>Defecto</strong>
                        </th>
                        <th style="padding:5px 10px 5px 5px; border-bottom: 10px solid silver; background-color: #a24689;">
                            <strong>Cant. Revisada</strong>
                        </th>
                        <th style="padding:5px 10px 5px 5px; border-bottom: 10px solid silver; background-color: #a24689;">
                            <strong>Cant. Defectos</strong>
                        </th>
                        <th style="padding:5px 10px 5px 5px; border-bottom: 10px solid silver; background-color: #a24689;">
                            <strong>Codigo del producto</strong>
                        </th>
                        <th style="padding:5px 10px 5px 5px; border-bottom: 10px solid silver; background-color: #a24689;">
                            <strong>Producto</strong>
                        </th>
                        <th style="padding:5px 10px 5px 5px; border-bottom: 10px solid silver; background-color: #a24689;">
                            <strong>Centro de trabajo</strong>
                        </th>
                        <th style="padding:5px 10px 5px 5px; border-bottom: 10px solid silver; background-color: #a24689;">
                            <strong>Estado</strong>
                        </th>
                        <th style="padding:5px 10px 5px 5px; border-bottom: 10px solid silver; background-color: #a24689;">
                            <strong>Pedido</strong>
                        </th>
                    </tr>
                    %s
                    </tbody>
                </table>
            </div>
          """ % (date, self.env.user.company_id.name, table)
        return body_mail

    def email_alert_queality(self, body_mail=None, destinatarios=None):
        mail = self.env['mail.mail'].create({
            'subject': 'Alertas de calidad',
            'email_to': destinatarios,
            'headers': "{'Return-Path': u'odoo@gebesa.com'}",
            'body_html': body_mail,
            'auto_delete': True,
            'message_type': 'comment',
        })
        mail.send()

    def send_email_alert_queality(self):
        date = fields.Date.context_today(self) - timedelta(days=1)
        alerts = self.search([('date', '=', date)], order="sale_id desc, product_id asc")

        if not alerts:
            return

        table = ''
        for alert in alerts:
            table += """
                <tr style="font-size: 12px; font-family:'Arial';">
                    <td align="center" style="border-bottom: 1px solid silver; color: #000;">%s</td>
                    <td align="center" style="border-bottom: 1px solid silver; color: #000;">%s</td>
                    <td align="center" style="border-bottom: 1px solid silver; color: #000;">%s</td>
                    <td align="center" style="border-bottom: 1px solid silver; color: #000;">%s</td>
                    <td align="center" style="border-bottom: 1px solid silver; color: #000;">%s</td>
                    <td align="center" style="border-bottom: 1px solid silver; color: #000;">%s</td>
                    <td align="center" style="border-bottom: 1px solid silver; color: #000;">%s</td>
                    <td align="center" style="border-bottom: 1px solid silver; color: #000;">%s</td>
                    <td align="center" style="border-bottom: 1px solid silver; color: #000;">%s</td>
                    <td align="center" style="border-bottom: 1px solid silver; color: #000;">%s</td>
                </tr>
            """ % (
                alert.name, alert.title, alert.flaw_id.name, alert.qty_reviewed, alert.qty_rejected,
                alert.product_id.default_code, alert.product_id.name, alert.workcenter_id.name,
                alert.stage_id.name, (alert.sale_id.name or ''))

        body_mail = self.get_html_body_send_email_alert_queality(table, date)
        destinatarios = self.env['ir.config_parameter'].sudo().get_param('send_alert.alert_queality', 'False')
        self.email_alert_queality(body_mail, destinatarios)
