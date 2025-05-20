# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    no_petition_needed = fields.Boolean(
        string='No petition number needed',
        default=False
    )

    @api.model
    def send_email_petition_number(self):
        invoice_ids = self.search([
            ('no_petition_needed', '=', False),
            ('petition_number', '=', None),
            ('partner_id.country_id.code', '!=', 'MX'),
            ('state', 'not in', ['draft', 'cancel']),
            ('type', '=', 'out_invoice'),
            ('date_invoice', '>', '2017-12-31')],
            order='date_invoice', limit=800)
        table = ''
        for inv in invoice_ids:
            table += """
                <tr><td style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                    <td style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                    <td style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                    <td align="right" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">$ %s</td></tr>
            """ % (inv.number, inv.date_invoice, inv.partner_id.name,
                   round(inv.amount_total, 2))
        mail_obj = self.env['mail.mail']
        body_mail = u"""
            <div summary="o_mail_notification" style="padding:0px; width:90%%;
             margin:0 auto; background: #FFFFFF repeat top /100%%; color:#777777">
                <table cellspacing="0" cellpadding="0" style="width:100%%;
                border-collapse:collapse;">
                    <tbody><tr>
                        <td valign="center" width="270" style="padding:5px 10px
                         5px 5px;font-size: 17px; font-family:'Arial';">
                            <b>Las siguientes facturas no tienen número de pedimento</b>
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
                            <th width="14%%" style="background-color: #a24689; color: #fff; padding:5px 10px 5px 5px;
                            font-size: 14px; font-family:'Arial'; border-bottom: 10px solid silver;"><strong>Folio</strong></th>
                            <th width="13%%" style="background-color: #a24689; color: #fff; padding:5px 10px 5px 5px;
                            font-size: 14px; font-family:'Arial'; border-bottom: 10px solid silver;"><strong>Fecha</strong></th>
                            <th width="60%%" style="background-color: #a24689; color: #fff; padding:5px 10px 5px 5px;
                            font-size: 14px; font-family:'Arial'; border-bottom: 10px solid silver;"><strong>Cliente</strong></th>
                            <th width="13%%" style="background-color: #a24689; color: #fff; padding:5px 10px 5px 5px;
                            font-size: 14px; font-family:'Arial'; border-bottom: 10px solid silver;"><strong>Total</strong></th>
                        </tr>
                        %s
                    </tbody>
                </table>
            </div>
        """ % (self.env.user.company_id.name, table)
        destinatarios = self.env['ir.config_parameter'].sudo().get_param('invoice_petition_control.receivers_email', 'False')
        mail = mail_obj.create({
            'subject': 'Facturas sin número de pedimento',
            'email_to': destinatarios,
            # 'email_to': 'juan.quinones@gebesa.com,esmeralda.gutierrez@gebesa.com,andrea.mejia@gebesa.com,alejandra.caballero@gebesa.com,sistemas@gebesa.com',
            'headers': "{'Return-Path': u'odoo@gebesa.com'}",
            'body_html': body_mail,
            'auto_delete': True,
            'message_type': 'comment',
            'model': 'account.invoice',
            # 'res_id': invoice_ids[0].id,
        })
        mail.send()
