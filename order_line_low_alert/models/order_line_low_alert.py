# -*- coding: utf-8 -*-

from datetime import date, timedelta
from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def send_sale_order_create(self):
        yesterday = fields.Date.to_string(date.today() - timedelta(days=1))
        today = fields.Date.to_string(date.today())
        companys = self.env['res.company'].search(
            [('is_manufacturer', '=', True)])

        for company in companys:
            destinatarios = self.env['ir.config_parameter'].sudo().get_param('order_line_low_alert.receivers_email_dest_company_' + str(company.id), 'False')

            sale_order = self.env['sale.order'].search([
                ('date_validator', '>=', yesterday),
                ('date_validator', '<=', today),
                ('company_id', '=', 1),
                ('state', '=', 'done')
            ])

            lines = sale_order.mapped('order_line').filtered(lambda l: l.profit_margin < 25)
            # destdefault = 'cesar.barron@gebesa.com,deysy.mascorro@gebesa.com,samuel.barron@gebesa.com,boyardo@gebesa.com,rogelio.lares@gebesa.com'
            table = ''
            for rec in lines:
                table += """
                    <tr>
                        <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                        <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                        <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                        <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                        <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">$%s</td>
                        <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">$%s</td>
                        <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s %%</td>
                        <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                    </tr>
                """ % (
                    rec.order_id.name,
                    rec.order_id.partner_id.name,
                    rec.order_id.user_id.name,
                    rec.name,
                    '{:,.2f}'.format(rec.product_id.standard_price),
                    '{:,.2f}'.format(rec.net_sale_mx / rec.product_uom_qty),
                    '{:,.2f}'.format((1 - (rec.product_id.standard_price / (rec.net_sale_mx/rec.product_uom_qty)))*100),
                    rec.margin_justification or '')
            if table:
                body_mail = self.get_html_body_sale_create(table, company)
                # destinatarios = destdefault
                self.send_alert_sale_create(body_mail, destinatarios)

    def get_html_body_sale_create(self, table=None, company=False):
        if not company:
            company = self.env.user.company_id
        body_mail = u"""
            <div summary="o_mail_notification" style="padding:0px; width:90%%;
                margin:0 auto; background: #FFFFFF repeat top /100%%; color:#777777">
                <table cellspacing="0" cellpadding="0" style="width:100%%;
                border-collapse:collapse;">
                    <tbody><tr>
                        <td valign="center" width="270" style="padding:5px 10px
                         5px 5px;font-size: 17px; font-family:'Arial';">
                            <b>Lineas de pedido con margen Menor a 25</b>
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
                    <tbody><tr>
                        <th width="10%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial'; 
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Folio de Pedido</strong></th>
                        <th width="6%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Nombre de Cliente</strong></th>
                        <th width="7%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial'; 
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Usuario que Validó</strong></th>
                        <th width="6%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial'; 
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Nombre del Producto</strong></th>
                        <th width="6%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial'; 
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Costo</strong></th>
                        <th width="6%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial'; 
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Precio Unitario</strong></th>
                        <th width="6%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial'; 
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Margen de la Línea</strong></th>
                        <th width="6%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial'; 
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Justificación Margen Bajo</strong></th>
                    </tr>
                    %s
                    </tbody>
                </table>
            </div>
          """ % (company.name, table)
        return body_mail

    def send_alert_sale_create(self, body_mail=None, destinatarios=None):
        mail = self.env['mail.mail'].create({
            'subject': 'Pedidos validados con línea de pedido por debajo del 25% de margen',
            'email_to': destinatarios,
            'headers': "{'Return-Path': u'odoo@gebesa.com'}",
            'body_html': body_mail,
            'auto_delete': True,
            'message_type': 'comment',
        })
        mail.send()
