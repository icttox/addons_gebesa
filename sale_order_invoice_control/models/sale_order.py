# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime, timedelta
from odoo import api, models


class AccountInvoice(models.Model):
    _inherit = 'sale.order'

    @api.model
    def send_email_petition_sale_order_number(self):
        self._cr.execute("""SELECT so.name,
                                CASE WHEN so.invoice_status = 'invoiced' THEN 'Facturado'
                                     WHEN so.invoice_status = 'to invoice' THEN 'A Facturar'
                                     WHEN so.invoice_status = 'no' THEN 'Nada que Facturar' END,
                                CASE WHEN so.geb_invoice_status = 'no_invoice' THEN 'No Facturado'
                                     WHEN so.geb_invoice_status = 'partial_invoice' THEN 'Parcialmente Facturado'
                                     WHEN so.geb_invoice_status = 'total_invoice' THEN 'Totalmente Facturado' END,
                                rp.name, so.net_sale_rate_mex,
                                (SELECT SUM(sm.product_uom_qty * sm.price_unit)
                                    FROM stock_move as sm
                                    WHERE sm.picking_id = sp.id),
                                so.total_cost,
                                CASE WHEN (SELECT SUM(ai.total_cost) FROM account_invoice as ai
                                    WHERE ai.sale_id = so.id
                                        AND to_char(ai.date_invoice,'YYYY-mm-dd') = to_char(CURRENT_TIMESTAMP - CAST('1 days' as interval), 'YYYY-mm-dd')) IS NULL
                                    THEN 0.00
                                    ELSE (SELECT SUM(ai.total_cost) FROM account_invoice as ai
                                            WHERE ai.sale_id = so.id
                                                AND to_char(ai.date_invoice,'YYYY-mm-dd') = to_char(CURRENT_TIMESTAMP - CAST('1 days' as interval), 'YYYY-mm-dd')) END,
                                    sp.name,
                                    (SELECT STRING_AGG(ai2.number, ',') FROM account_invoice as ai2
                                            WHERE ai2.sale_id = so.id
                                                AND to_char(ai2.date_invoice,'YYYY-mm-dd') = to_char(CURRENT_TIMESTAMP - CAST('1 days' as interval), 'YYYY-mm-dd'))
                                FROM sale_order as so
                                    LEFT JOIN stock_picking as sp ON (sp.sale_id = so.id)
                                    LEFT JOIN res_partner as rp ON (rp.id = so.partner_id)
                                WHERE sp.location_dest_id = 9
                                    AND to_char(sp.date_done,'YYYY-mm-dd') = to_char(CURRENT_TIMESTAMP - CAST('1 days' as interval), 'YYYY-mm-dd')
                                ORDER BY so.name"""),
        res = False
        if self._cr.rowcount:
            res = self._cr.fetchall()
        table = ''
        if res:
            for sal in res:
                table += """
                    <tr><td style="font-size: 12px; color: #000; font-family:'Arial'; border-bottom: 1px solid silver;">%s</td>
                        <td style="font-size: 12px; color: #000; font-family:'Arial'; border-bottom: 1px solid silver;">%s</td>
                        <td style="font-size: 12px; color: #000; font-family:'Arial'; border-bottom: 1px solid silver;">%s</td>
                        <td style="font-size: 12px; color: #000; font-family:'Arial'; border-bottom: 1px solid silver;">%s</td>
                        <td align="right" style="font-size: 12px; color: #000; font-family:'Arial'; border-bottom: 1px solid silver;">$%s</td>
                        <td align="right" style="font-size: 12px; color: #000; font-family:'Arial'; border-bottom: 1px solid silver;">$%s</td>
                        <td align="right" style="font-size: 12px; color: #000; font-family:'Arial'; border-bottom: 1px solid silver;">$%s</td>
                        <td align="right" style="font-size: 12px; color: #000;font-family:'Arial'; border-bottom: 1px solid silver;">$%s</td>
                        <td align="center" style="font-size: 12px; color: #000;font-family:'Arial'; border-bottom: 1px solid silver;">%s</td>
                        <td align="right" style="font-size: 12px; color: #000;font-family:'Arial'; border-bottom: 1px solid silver;">%s</td></tr>
                """ % (sal[0], sal[1], sal[2], sal[3], round(sal[4], 2), round(sal[5], 2), round(sal[6], 2), round(sal[7], 2), sal[8], sal[9])
        mail_obj = self.env['mail.mail']
        body_mail = u"""
            <div summary="o_mail_notification" style="padding:0px; width:90%%;
             margin:0 auto; background: #FFFFFF repeat top /100%%; color:#777777">
                <table cellspacing="0" cellpadding="0" style="width:100%%;
                border-collapse:collapse;">
                    <tbody><tr>
                        <td valign="center" width="270" style="padding:5px 10px
                         5px 5px;font-size: 17px; font-family:'Arial';">
                            <b>Las Siguientes Pedidos Fueron Facturados el Dia %s</b>
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
                        <th width="9%%" style="background-color: #a24689; color: #fff; padding:5px 10px 5px 5px;font-size: 14px;
                        border-bottom: 10px solid silver; font-family:'Arial';"><strong>Folio</strong></th>
                        <th width="12%%" style="background-color: #a24689; color: #fff; padding:5px 10px 5px 5px;font-size: 14px;
                        border-bottom: 10px solid silver; font-family:'Arial';"><strong>Estatus Ultima Entrega</strong></th>
                        <th width="12%%" style="background-color: #a24689; color: #fff; padding:5px 10px 5px 5px;font-size: 14px;
                        border-bottom: 10px solid silver; font-family:'Arial';"><strong>Estatus Facturación Pedido</strong></th>
                        <th width="29%%" style="background-color: #a24689; color: #fff; padding:5px 10px 5px 5px;font-size: 14px;
                        border-bottom: 10px solid silver; font-family:'Arial';"><strong>Cliente</strong></th>
                        <th width="12%%" style="background-color: #a24689; color: #fff; padding:5px 10px 5px 5px;font-size: 14px;
                        border-bottom: 10px solid silver; font-family:'Arial';"><strong>Venta Neta Pedido</strong></th>
                        <th width="12%%" style="background-color: #a24689; color: #fff; padding:5px 10px 5px 5px;font-size: 14px;
                        border-bottom: 10px solid silver; font-family:'Arial';"><strong>Total Move</strong></th>
                        <th width="12%%" style="background-color: #a24689; color: #fff; padding:5px 10px 5px 5px;font-size: 14px;
                        border-bottom: 10px solid silver; font-family:'Arial';"><strong>Costo Total Pedido</strong></th>
                        <th width="12%%" style="background-color: #a24689; color: #fff; padding:5px 10px 5px 5px;font-size: 14px;
                        border-bottom: 10px solid silver; font-family:'Arial';"><strong>Costo Total Factura</strong></th>
                        <th width="12%%" style="background-color: #a24689; color: #fff; padding:5px 10px 5px 5px;font-size: 14px;
                        border-bottom: 10px solid silver; font-family:'Arial';"><strong>Movimiento</strong></th>
                        <th width="3%%" style="background-color: #a24689; color: #fff; padding:5px 10px 5px 5px;font-size: 14px;
                        border-bottom: 10px solid silver; font-family:'Arial';"><strong>Facturas</strong></th>
                    </tr>
                    %s
                    </tbody>
                </table>
            </div>
        """ % (datetime.now() - timedelta(days=1), self.env.user.company_id.name, table)
        mail = mail_obj.create({
            'subject': 'Pedidos No Facturados',
            'email_to': 'sistemas@gebesa.com',
            'headers': "{'Return-Path': u'odoo@gebesa.com'}",
            'body_html': body_mail,
            'auto_delete': True,
            'message_type': 'comment',
            'model': 'sale.order',
            # 'res_id': invoice_ids[0].id,
        })
        mail.send()
