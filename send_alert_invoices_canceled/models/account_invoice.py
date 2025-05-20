# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import datetime
from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def send_invoice_cancel(self):
        now = datetime.datetime.now()
        # date_init = str(now.year) + '-' + str(now.month - 6) + '-' + str(now.day - 6)
        date = datetime.datetime(now.year, now.month, 1)
        fecha = fields.Date.to_string(date)
        invoice = self.env['account.invoice'].search([('type', '=', 'out_invoice'), ('date_invoice', '=', fecha), ('state', '=', 'cancel')])
        # company = invoice.mapped('company_id')
        # destdefault = 'cesar.barron@gebesa.com,deysy.mascorro@gebesa.com,samuel.barron@gebesa.com,salmon@gebesa.com'
        table1 = ''
        table2 = ''
        table3 = ''
        table4 = ''
        date_inv = ''
        date_can = ''
        date_inv_llc = ''
        date_can_llc = ''
        date_inv_gbl = ''
        date_can_gbl = ''
        date_inv_slm = ''
        date_can_slm = ''
        mpf = invoice.filtered(lambda inv: inv.company_id.id == 1)
        llc = invoice.filtered(lambda inv: inv.company_id.id == 10)
        glb = invoice.filtered(lambda inv: inv.company_id.id == 4)
        slm = invoice.filtered(lambda inv: inv.company_id.id == 3)

        for rec_mpf in mpf:
            if not rec_mpf.date_invoice or not rec_mpf.date_cancelled:
                date_inv = '---'
                date_can = '---'
            else:
                date_inv = rec_mpf.date_invoice
                date_can = rec_mpf.date_cancelled
            table1 += """
            <tr>
                <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">$%s</td>
            </tr>
                """ % (str(rec_mpf.partner_id.name), str(date_inv), str(date_can), rec_mpf.number_cancel, '{:,.2f}'.format(rec_mpf.amount_total))
        for rec_llc in llc:
            if not rec_llc.date_invoice or not rec_llc.date_cancelled:
                date_inv_llc = '---'
                date_can_llc = '---'
            else:
                date_inv_llc = rec_llc.date_invoice
                date_can_llc = rec_llc.date_cancelled
            table2 += """
            <tr>
                <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">$%s</td>
            </tr>
                """ % (str(rec_llc.partner_id.name), str(date_inv_llc), str(date_can_llc), rec_llc.number_cancel, '{:,.2f}'.format(rec_llc.amount_total))
        for rec_glb in glb:
            if not rec_glb.date_invoice or not rec_glb.date_cancelled:
                date_inv_gbl = '---'
                date_can_gbl = '---'
            else:
                date_inv_gbl = rec_glb.date_invoice
                date_can_gbl = rec_glb.date_cancelled
            table3 += """
            <tr>
                <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">$%s</td>
            </tr>
                """ % (str(rec_glb.partner_id.name), str(date_inv_gbl), str(date_can_gbl), rec_glb.number_cancel, '{:,.2f}'.format(rec_glb.amount_total))
        for rec_slm in slm:
            if not rec_slm.date_invoice or not rec_slm.date_cancelled:
                date_inv_slm = '---'
                date_can_slm = '---'
            else:
                date_inv_slm = rec_slm.date_invoice
                date_can_slm = rec_slm.date_cancelled
            table4 += """
            <tr>
                <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">$%s</td>
            </tr>
                """ % (str(rec_slm.partner_id.name), str(date_inv_slm), str(date_can_slm), rec_slm.number_cancel, '{:,.2f}'.format(rec_slm.amount_total))
        if table1 and table2 and table3 and table4:
            body_mail = self.get_html_body_invoice_canceled(table1, table2, table3, table4)
            # destinatarios = destdefault
            destinatarios = self.env['ir.config_parameter'].sudo().get_param('send_alert_invoices_canceled.receivers_email', 'False')
            self.send_alert_invoice_canceled(body_mail, destinatarios)

    def get_html_body_invoice_canceled(self, table1=None, table2=None, table3=None, table4=None, company=False):
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
                            <b>Reporte de Cancelaciones por Compañia</b>
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
            </div>
            <div style="padding:0px; width:100%%; margin:0 auto; background:
            #FFFFFF repeat top /100%%; color:#fff">
                <table style="border-collapse:collapse; margin: 0 auto; width:
                90%%; background:inherit; color:inherit">
                    <tbody>
                    <tr>
                        <h2 style="font-size:18px; font-family:'Arial'; color: #a24689;">
                            Manufacturas<b style="font-size:16px;"></b>
                        </h2>
                    </tr>
                    <tr>
                        <th width="10%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Cliente</strong></th>
                        <th width="6%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Fecha de Factura</strong></th>
                        <th width="7%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Fecha de Cancelación</strong></th>
                        <th width="7%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Folio</strong></th>
                        <th width="6%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Total</strong></th>
                    </tr>
                    %s
                    </tbody>
                </table>
                <br/><br/>
                <table style="border-collapse:collapse; margin: 0 auto; width:
                90%%; background:inherit; color:inherit">
                    <tbody>
                    <tr>
                        <h2 style="font-size:18px; font-family:'Arial'; color: #a24689;">
                            Gebesa LLC<b style="font-size:16px;"></b>
                        </h2>
                    </tr>
                    <tr>
                        <th width="10%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Cliente</strong></th>
                        <th width="6%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Fecha de Factura</strong></th>
                        <th width="7%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Fecha de Cancelación</strong></th>
                        <th width="7%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Folio</strong></th>
                        <th width="6%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Total</strong></th>
                    </tr>
                    %s
                    </tbody>
                </table>
                <br/><br/>
                <table style="border-collapse:collapse; margin: 0 auto; width:
                90%%; background:inherit; color:inherit">
                    <tbody>
                    <tr>
                        <h2 style="font-size:18px; font-family:'Arial'; color: #a24689;">
                            Transportes Galbo<b style="font-size:16px;"></b>
                        </h2>
                    </tr>
                    <tr>
                        <th width="10%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Cliente</strong></th>
                        <th width="6%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Fecha de Factura</strong></th>
                        <th width="7%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Fecha de Cancelación</strong></th>
                        <th width="7%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Folio</strong></th>
                        <th width="6%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Total</strong></th>
                    </tr>
                    %s
                    </tbody>
                </table>
                <br/><br/>
                <table style="border-collapse:collapse; margin: 0 auto; width:
                90%%; background:inherit; color:inherit">
                    <tbody>
                    <tr>
                        <h2 style="font-size:18px; font-family:'Arial'; color: #a24689;">
                            Salmón<b style="font-size:16px;"></b>
                        </h2>
                    </tr>
                    <tr>
                        <th width="10%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Cliente</strong></th>
                        <th width="6%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Fecha de Factura</strong></th>
                        <th width="7%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Fecha de Cancelación</strong></th>
                        <th width="7%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Folio</strong></th>
                        <th width="6%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Total</strong></th>
                    </tr>
                    %s
                    </tbody>
                </table>
            </div>
          """ % (self.env.user.company_id.name, table1, table2, table3, table4)
        return body_mail

    def send_alert_invoice_canceled(self, body_mail=None, destinatarios=None):
        mail = self.env['mail.mail'].create({
            'subject': 'Reporte de Cancelaciones por Compañia',
            'email_to': destinatarios,
            'headers': "{'Return-Path': u'odoo@gebesa.com'}",
            'body_html': body_mail,
            'auto_delete': True,
            'message_type': 'comment',
        })
        mail.send()
