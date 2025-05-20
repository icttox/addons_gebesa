# Copyright 2022, Marco Esquivel
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class SendAlertBilledOrdersWhitMo(models.Model):
    _inherit = 'account.invoice'

    def _data_send_alert_billed_orders_whit_mo(self):
        self._cr.execute(
            """
            SELECT so.name AS pedido,
            ai.date_invoice AS fecha_factura,
            so.state AS status_pedido,
            mp.name AS mo,
            CONCAT('[', pp.default_code, '] ', pp.name_template) AS articulo_completo,
            sr.name AS produccion,
            mp.product_qty AS cantidad,
            mp.state AS status
            FROM account_invoice AS ai
            LEFT JOIN sale_order AS so ON ai.sale_id = so.id
            LEFT JOIN mrp_production AS mp ON mp.sale_id = so.id
            LEFT JOIN product_product AS pp ON pp.id = mp.product_id
            LEFT JOIN stock_rule AS sr on sr.id = mp.rule_id
            WHERE ai.sale_id is not null
            AND ai.type = 'out_invoice'
            AND ai.date_invoice >= CURRENT_DATE - INTERVAL '1 year' - INTERVAL '15 days'
            AND ai.date_invoice <= CURRENT_DATE - INTERVAL '15 days'
            AND ai.state not in ('draf','cancel')
            AND ai.prepayment_ok = false
            AND mp.state not in ('transfer','cancel')
            AND so.geb_invoice_status = 'total_invoice'
            ORDER BY ai.date_invoice,so.id,mp.id
            """,)
        if not self._cr.rowcount:
            return []
        return self._cr.fetchall()

    @api.model
    def send_alert_billed_orders_whit_mo(self):
        orders = self._data_send_alert_billed_orders_whit_mo()
        table = ''

        if not orders:
            return
        for order in orders:
            table += """
                <tr>
                    <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                    <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                    <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                    <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                    <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                    <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                    <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                    <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                </tr>
            """ % (
                order[0], order[1], order[2], order[3], order[4], order[5], order[6], order[7])

        body_mail = self.get_html_body_send_alert_billed_orders_whit_mo(table)
        destinatarios = self.env['ir.config_parameter'].sudo().get_param('send_alert.billed_orders_whit_mo', 'False')
        self.alert_billed_orders_whit_mo(body_mail, destinatarios)

    def get_html_body_send_alert_billed_orders_whit_mo(self, table=None):
        body_mail = u"""
            <div summary="o_mail_notification" style="padding:0px; width:90%%;
                margin:0 auto; background: #FFFFFF repeat top /100%%; color:#777777">
                <table cellspacing="0" cellpadding="0" style="width:100%%;
                border-collapse:collapse;">
                    <tbody><tr>
                        <td valign="center" width="270" style="padding:5px 10px
                         5px 5px;font-size: 17px; font-family:'Arial';">
                            <b>Alerta de pedidos facturados con MO en estatus no traspasado ni cancelado</b>
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
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Pedido</strong></th>
                        <th width="10%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Fecha factura</strong></th>
                        <th width="6%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Estatus pedido</strong></th>
                        <th width="6%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>MO</strong></th>
                        <th width="6%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Producto MO</strong></th>
                        <th width="6%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Ruta fabricación MO</strong></th>
                        <th width="6%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Cantidad MO</strong></th>
                        <th width="6%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Estatus MO</strong></th>
                    </tr>
                    %s
                    </tbody>
                </table>
            </div>
          """ % (self.env.user.company_id.name, table)
        return body_mail

    def alert_billed_orders_whit_mo(self, body_mail=None, destinatarios=None):
        mail = self.env['mail.mail'].create({
            'subject': 'Pedidos facturados con MO en estatus no traspasado ni cancelado',
            'email_to': destinatarios,
            'headers': "{'Return-Path': u'odoo@gebesa.com'}",
            'body_html': body_mail,
            'auto_delete': True,
            'message_type': 'comment',
        })
        mail.send()
