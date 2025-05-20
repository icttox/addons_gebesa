# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import date, timedelta
from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def send_invoice_created(self):
        yesterday = fields.Date.to_string(date.today() - timedelta(days=1))

        companys = self.env['res.company'].search(
            [('is_manufacturer', '=', True)])

        for company in companys:
            invoices = self.search([
                ('type', '=', 'in_invoice'),
                ('date_invoice', '=', yesterday),
                ('state', 'in', ('open', 'paid')),
                ('company_id', '=', company.id)])

            # destdefault = 'cesar.barron@gebesa.com,deysy.mascorro@gebesa.com,samuel.barron@gebesa.com,'
            accounts = {
                '500.02',
                '500.03',
                '500.04'
            }

            for acc in accounts:
                destinatarios = self.env['ir.config_parameter'].sudo().get_param('send_alert_invoices_created.receivers_email_dest_' + str(acc), 'False')

                table = ''
                account = self.env['account.account'].search([
                    ('code', '=', acc),
                    ('company_id', '=', company.id)
                ])

                inv_line = self.env['account.invoice.line'].search([
                    ('account_id', 'child_of', account.id),
                    ('invoice_id', 'in', invoices.ids)
                ])

                if not inv_line:
                    continue

                for line in inv_line:
                    if line.invoice_id.state == 'paid':
                        inv_state = 'pagado'
                    if line.invoice_id.state == 'open':
                        inv_state = 'abierto'

                    table += """
                        <tr>
                            <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                            <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                            <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                            <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                            <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">$%s</td>
                            <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                            <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                        </tr>
                    """ % (
                        line.invoice_id.partner_id.name,
                        line.invoice_id.date_invoice, line.invoice_id.number,
                        line.name, '{:,.2f}'.format(line.price_subtotal),
                        line.create_uid.name, inv_state)

                body_mail = self.get_html_body_invoice_created(table, company)
                # destinatarios = destdefault + accounts[acc]
                self.send_alert_invoice_created(body_mail, destinatarios)

    def get_html_body_invoice_created(self, table=None, company=False):
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
                            <b>Facturas</b>
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
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Cliente</strong></th>
                        <th width="6%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Fecha</strong></th>
                        <th width="7%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Folio</strong></th>
                        <th width="7%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Concepto</strong></th>
                        <th width="6%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Total</strong></th>
                        <th width="6%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Registro</strong></th>
                        <th width="12%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Estatus</strong></th>
                    </tr>
                    %s
                    </tbody>
                </table>
            </div>
          """ % (company.name, table)
        return body_mail

    def send_alert_invoice_created(self, body_mail=None, destinatarios=None):
        mail = self.env['mail.mail'].create({
            'subject': 'Facturas de proveedor del dia de ayer',
            'email_to': destinatarios,
            'headers': "{'Return-Path': u'odoo@gebesa.com'}",
            'body_html': body_mail,
            'auto_delete': True,
            'message_type': 'comment',
        })
        mail.send()

    @api.model
    def send_invoice_create(self):
        yesterday = fields.Date.to_string(date.today() - timedelta(days=1))
        companys = self.env['res.company'].search(
            [('is_manufacturer', '=', True)])
        for company in companys:
            invoice = self.env['account.invoice'].search([
                ('type', '=', 'in_invoice'),
                ('date_invoice', '=', yesterday),
                # ('purchase_ids', '!=', False),
                ('state', 'in', ('open', 'paid')),
                ('create_uid', 'in', (525, 476))
            ])
            # destdefault = 'cesar.barron@gebesa.com,deysy.mascorro@gebesa.com,samuel.barron@gebesa.com,salmon@gebesa.com'
            # destdefault_b = 'cesar.barron@gebesa.com,deysy.mascorro@gebesa.com,samuel.barron@gebesa.com,sebastian@gebesa.com'

            invoices_m = invoice.filtered(lambda inv: inv.create_uid.id == 525)

            invoices_a = invoice.filtered(lambda inv: inv.create_uid.id == 476 and inv.account_analytic_id.id == 179 and not inv.purchase_ids)

            table = ''
            for rec in invoices_m:
                concepto_m = ', '.join(rec.invoice_line_ids.mapped('name'))
                table += """
                    <tr>
                        <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                        <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                        <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                        <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                        <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                        <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">$%s</td>
                        <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                        <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                        <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                    </tr>
                """ % (
                    str(rec.partner_id.name),
                    str(rec.date_invoice),
                    rec.number,
                    concepto_m,
                    str(rec.comment),
                    '{:,.2f}'.format(rec.amount_total),
                    str(rec.create_uid.name),
                    str(rec.account_analytic_id.name),
                    rec.state)
            if table:
                body_mail = self.get_html_body_invoice_create(table, company)
                # destinatarios = destdefault
                destinatarios = self.env['ir.config_parameter'].sudo().get_param('send_alert_invoices_created_a.receivers_email', 'False')
                self.send_alert_invoice_create(body_mail, destinatarios, 'Facturas de MP Rodrigo Rangel')
            table = ''
            for reco in invoices_a:
                concepto = ', '.join(reco.invoice_line_ids.mapped('name'))
                table += """
                    <tr>
                        <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                        <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                        <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                        <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                        <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                        <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">$%s</td>
                        <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                        <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                        <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                    </tr>
                """ % (
                    str(reco.partner_id.name),
                    str(reco.date_invoice),
                    reco.number,
                    concepto,
                    str(reco.comment),
                    '{:,.2f}'.format(reco.amount_total),
                    str(reco.create_uid.name),
                    str(reco.account_analytic_id.name),
                    reco.state)
            if table:
                body_mail = self.get_html_body_invoice_create(table, company)
                # destinatarios = destdefault_b
                destinatarios = self.env['ir.config_parameter'].sudo().get_param('send_alert_invoices_created_b.receivers_email', 'False')
                self.send_alert_invoice_create(body_mail, destinatarios, 'Facturas correspondientes a Katia Reyes')

    def get_html_body_invoice_create(self, table=None, company=False):
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
                            <b>Facturas</b>
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
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Cliente</strong></th>
                        <th width="6%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Fecha</strong></th>
                        <th width="7%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Folio</strong></th>
                        <th width="7%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Concepto</strong></th>
                        <th width="7%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Notas</strong></th>
                        <th width="6%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Total</strong></th>
                        <th width="6%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Registro</strong></th>
                        <th width="6%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Centro de Costos</strong></th>
                        <th width="12%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Estatus</strong></th>
                    </tr>
                    %s
                    </tbody>
                </table>
            </div>
          """ % (company.name, table)
        return body_mail

    def send_alert_invoice_create(self, body_mail=None, destinatarios=None, titulo=None):
        mail = self.env['mail.mail'].create({
            'subject': titulo,
            'email_to': destinatarios,
            'headers': "{'Return-Path': u'odoo@gebesa.com'}",
            'body_html': body_mail,
            'auto_delete': True,
            'message_type': 'comment',
        })
        mail.send()
