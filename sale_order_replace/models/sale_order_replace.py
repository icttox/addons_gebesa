# -*- coding: utf-8 -*-
# Copyright 2018, Esther Cisneros
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import timedelta

from odoo import api, fields, models


class SaleOrder(models.Model):

    _name = 'sale.order'
    _inherit = 'sale.order'

    order_replaced = fields.Many2one(
        'sale.order',
        string="Order that replaces",
    )

    date_cancelled = fields.Date(
        string="Cancellation Date/Closed",
    )

    @api.multi
    def action_cancel(self):
        for order in self:
            order.date_cancelled = fields.Date.today()
        super().action_cancel()

    @api.multi
    def action_closed(self):
        for order in self:
            order.date_cancelled = fields.Date.today()
        super().action_closed()

    @api.model
    def send_email_orders_canceled(self):
        lim_date = timedelta(days=1)
        date_today = fields.Date.today()
        ddd = fields.Datetime.from_string(date_today)
        date_cancel = ddd - lim_date
        order_ids = self.search([
            ('state', 'not in', ['done', 'draft', 'sent']),
            ('date_cancelled', '=', date_cancel)])
        table = ''
        remp_date = ''
        remp_ord = ''
        rel_seg = ''
        rel_seg_repla = ''
        for res in order_ids:
            if not res.date_cancelled:
                remp_date = '---'
            else:
                remp_date = res.date_cancelled
            if not res.order_replaced:
                remp_ord = '---'
            else:
                remp_ord = res.order_replaced.name
            if not res.related_segment:
                rel_seg = '---'
            else:
                rel_seg = res.related_segment
            if not res.order_replaced.related_segment:
                rel_seg_repla = '---'
            else:
                rel_seg_repla = res.order_replaced.related_segment
            table += """

                <div>
                    <style type="text/css">
                        tr {
                        font-family: 'Arial';
                            color: #000000;
                        }
                        strong {
                            font-size: 14px;
                        }
                    </style>
                </div>
                <tr align="center"><td style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';"">%s</td>
                    <td style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';"">%s</td>
                    <td style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';"">%s</td>
                    <td style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';"">%s</td>
                    <td style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';"">%s</td>
                    <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';"">
                    %s</td>
                </tr>
            """ % (remp_date, res.partner_id.name, res.name, remp_ord, rel_seg, rel_seg_repla)
        mail_obj = self.env['mail.mail']
        body_mail = u"""
            <div summary="o_mail_notification" style="padding:0px; width:90%%;
             margin:0 auto; background: #FFFFFF repeat top /100%%; color:#777777">
                <table cellspacing="0" cellpadding="0" style="width:100%%;
                border-collapse:collapse;">
                    <tbody><tr>
                        <td valign="center" width="270" style="padding:5px 10px
                         5px 5px;font-size: 17px; font-family:'Arial';">
                            <b>Los siguientes pedidos fueron Cancelados y/o Cerrados</b>
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
                        <th width="12%%" style="background-color: #a24689; color: #fff; padding:5px 10px 5px 5px;font-size: 14px;
                        border-bottom: 10px solid silver; font-family:'Arial';"><strong>
                        Fecha de Cancelacion y/o Cerrado</strong></th>
                        <th width="40%%" style="background-color: #a24689; color: #fff; padding:5px 10px 5px 5px;font-size: 14px;
                        border-bottom: 10px solid silver; font-family:'Arial';"><strong>
                        Cliente</strong></th>
                        <th width="14%%" style="background-color: #a24689; color: #fff; padding:5px 10px 5px 5px;font-size: 14px;
                        border-bottom: 10px solid silver; font-family:'Arial';"><strong>
                        Pedido</strong></th>
                        <th width="20%%" style="background-color: #a24689; color: #fff; padding:5px 10px 5px 5px;font-size: 14px;
                        border-bottom: 10px solid silver; font-family:'Arial';"><strong>
                        Segmento(s) Relacionado(s)</strong></th>
                        <th width="14%%" style="background-color: #a24689; color: #fff; padding:5px 10px 5px 5px;font-size: 14px;
                        border-bottom: 10px solid silver; font-family:'Arial';"><strong>
                        Pedido que Sustituye</strong></th>
                        <th width="22%%" style="background-color: #a24689; color: #fff; padding:5px 10px 5px 5px;font-size: 14px;
                        border-bottom: 10px solid silver; font-family:'Arial';"><strong>
                        Seg. Rel. Pedido Sustituye</strong></th>
                    </tr>
                    %s
                    </tbody>
                </table>
            </div>
          """ % (self.env.user.company_id.name, table)
        destinatarios = self.env['ir.config_parameter'].sudo().get_param('sale_order_replace.receivers_email', 'False')
        mail = mail_obj.create({
            'subject': 'Pedidos Cancelados y/o Cerrados',
            'email_to': destinatarios,
            # 'email_to': 'equipocompras@gebesa.com,sistemas@gebesa.com,brandon.ramirez@gebesa.com,miguel.martinez@gebesa.com,victor.campos@gebesa.com,elizabeth.valenzuela@gebesa.com,cristina.rodriguez@gebesa.com,julio.delarosa@gebesa.com',
            'headers': "{'Return-Path': u'odoo@gebesa.com'}",
            'body_html': body_mail,
            'auto_delete': True,
            'message_type': 'comment',
            'model': 'sale.order',
            # 'res_id': order_ids[0].id,
        })
        mail.send()
