# Copyright 2024, Marco Esquivel
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class SendAlertInvoiceWithSomeDiscountLine(models.Model):
    _inherit = 'account.invoice.line'

    def _data_send_alert_invoice_with_some_discount_line(self):
        self._cr.execute(
            """
            SELECT
            ai.number AS folio_factura,
            rp.name AS cliente,
            ai.date_invoice AS fecha_factura,
            so.name AS pedido,
            ai.state AS estado_factura,
            ai.amount_total AS total_factura
            FROM account_invoice_line AS ail
            LEFT JOIN account_invoice AS ai ON ai.id = ail.invoice_id
            LEFT JOIN res_partner AS rp ON rp.id = ail.partner_id
            LEFT JOIN sale_order AS so ON ai.sale_id = so.id
            WHERE ai.company_id = 1
            AND ail.discount > 0
            AND ai.type = 'out_invoice'
            AND ai.date_invoice = CURRENT_DATE - INTERVAL '1 day'
            AND ai.state IN ('paid', 'open')
            GROUP BY ai.id, rp.id, so.id
            ORDER BY ai.id
            """,)
        if not self._cr.rowcount:
            return []
        return self._cr.fetchall()

    @api.model
    def send_alert_invoice_with_some_discount_line(self):
        invoices = self._data_send_alert_invoice_with_some_discount_line()
        table = ''

        if not invoices:
            return
        for invoice in invoices:
            table += """
                <tr>
                    <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                    <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                    <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                    <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                    <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                    <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">$ %s</td>
                </tr>
            """ % (
                invoice[0], invoice[1], invoice[2], invoice[3], invoice[4], '{:,.2f}'.format(invoice[5]))

        body_mail = self.get_html_body_send_alert_invoice_with_some_discount_line(table)
        destinatarios = self.env['ir.config_parameter'].sudo().get_param('send_alert.invoice_with_some_discount_line', 'False')
        self.alert_invoice_with_some_discount_line(body_mail, destinatarios)

    def get_html_body_send_alert_invoice_with_some_discount_line(self, table=None):
        body_mail = u"""
            <div summary="o_mail_notification" style="padding:0px; width:90%%;
                margin:0 auto; background: #FFFFFF repeat top /100%%; color:#777777">
                <table cellspacing="0" cellpadding="0" style="width:100%%;
                border-collapse:collapse;">
                    <tbody><tr>
                        <td valign="center" width="270" style="padding:5px 10px
                         5px 5px;font-size: 17px; font-family:'Arial';">
                            <b>Alerta de facturas con lineas con descuento</b>
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
                    <tr>
                        <th width="10%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Folio factura</strong></th>
                        <th width="10%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Cliente</strong></th>
                        <th width="6%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Fecha factura</strong></th>
                        <th width="6%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Pedido</strong></th>
                        <th width="6%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Estatus factura</strong></th>
                        <th width="6%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Total factura</strong></th>
                    </tr>
                    %s
                    </tbody>
                </table>
            </div>
          """ % (self.env.user.company_id.name, table)
        return body_mail

    def alert_invoice_with_some_discount_line(self, body_mail=None, destinatarios=None):
        mail = self.env['mail.mail'].create({
            'subject': 'Facturas con lineas de descuento',
            'email_to': destinatarios,
            'headers': "{'Return-Path': u'odoo@gebesa.com'}",
            'body_html': body_mail,
            'auto_delete': True,
            'message_type': 'comment',
        })
        mail.send()
