# -*- coding: utf-8 -*-
# Copyright 2018, Esther Cisneros
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import timedelta
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountInvoice(models.Model):

    _name = 'account.invoice'
    _inherit = 'account.invoice'

    invoice_replaced = fields.Many2one(
        'account.invoice',
        string="Invoice that replaces",
        copy=False,
    )

    date_cancelled = fields.Date(
        string="Cancellation Date",
        copy=False,
    )

    number_cancel = fields.Char(
        string=("Nombre de la factura cancelada"),
    )

    @api.onchange('invoice_replaced')
    def _onchange_invoice_replaced(self):
        if self.invoice_replaced:
            if self.invoice_replaced.l10n_mx_edi_cfdi_uuid:
                self.l10n_mx_edi_origin = '04|%s' % self.invoice_replaced.l10n_mx_edi_cfdi_uuid
            else:
                self.l10n_mx_edi_origin = ''
        else:
            self.l10n_mx_edi_origin = ''

    @api.multi
    def action_cancel(self):
        for inv in self:
            if inv.id == inv.invoice_replaced.id:
                raise UserError(_("Please select an invoice to substitute different to the invoice to be canceled"))
            inv.date_cancelled = fields.Date.today()
            inv.number_cancel = inv.number
        return super().action_cancel()

    @api.model
    def send_email_invoice_canceled(self):
        date_cancel = fields.Date.today()
        date_cancel = fields.Datetime.from_string(date_cancel)
        date_cancel = date_cancel - timedelta(days=1)
        inv_ids = self.search([
            ('state', '=', ['cancel']),
            ('company_id', '=', 1),
            ('type', '=', 'out_invoice'),
            ('date_cancelled', '=', date_cancel)])
        table = ''
        remp_date = ''
        remp_rep = ''
        for inve in inv_ids:
            if not inve.date_cancelled:
                remp_date = '---'
            else:
                remp_date = inve.date_cancelled
            if not inve.invoice_replaced:
                remp_rep = '---'
            else:
                remp_rep = inve.invoice_replaced.number
            table += """
                <tr>
                    <td style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                    <td style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                    <td style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                    <td align="right" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">
                    %s</td>
                </tr>
            """ % (remp_date, inve.partner_id.name, inve.number_cancel, remp_rep)
        destinatarios = self.env['ir.config_parameter'].sudo().get_param('cancelled_invoices_manufacturas.receivers_email', 'False')
        mail_obj = self.env['mail.mail']
        body_mail = u"""
            <div summary="o_mail_notification" style="padding:0px; width:90%%;
             margin:0 auto; background: #FFFFFF repeat top /100%%; color:#777777">
                <table cellspacing="0" cellpadding="0" style="width:100%%;
                border-collapse:collapse;">
                    <tbody><tr>
                        <td valign="center" width="270" style="padding:5px 10px
                         5px 5px;font-size: 17px; font-family:'Arial';">
                            <b>Las siguientes facturas ya fueron canceladas</b>
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
                        <th width="17%%" style="background-color: #a24689; color: #fff; padding:5px 10px 5px 5px;font-size: 14px;
                        border-bottom: 10px solid silver; font-family:'Arial';"><strong>Fecha de Cancelacion</strong></th>
                        <th width="50%%" style="background-color: #a24689; color: #fff; padding:5px 10px 5px 5px;font-size: 14px;
                        border-bottom: 10px solid silver; font-family:'Arial';"><strong>Cliente</strong></th>
                        <th width="17%%" style="background-color: #a24689; color: #fff; padding:5px 10px 5px 5px;font-size: 14px;
                        border-bottom: 10px solid silver; font-family:'Arial';"><strong>Factura Cancelada</strong></th>
                        <th width="17%%" style="background-color: #a24689; color: #fff; padding:5px 10px 5px 5px;font-size: 14px;
                        border-bottom: 10px solid silver; font-family:'Arial';"><strong>Factura que Sustituye</strong></th>
                    </tr>
                    %s
                    </tbody>
                </table>
            </div>
          """ % (self.env.user.company_id.name, table)

        mail = mail_obj.create({
            'subject': 'Facturas Canceladas',
            'email_to': destinatarios,
            # 'sergio.hernandez@gebesa.com,pedro.acosta@gebesa.com,monica.sanchez@gebesa.com,jesus.castrellon@gebesa.com,esmeralda.gutierrez@gebesa.com,sistemas@gebesa.com',
            'headers': "{'Return-Path': u'odoo@gebesa.com'}",
            'body_html': body_mail,
            'auto_delete': True,
            'message_type': 'comment',
            'model': 'account.invoice',
            # 'res_id': inv_ids[0].id,
        })
        mail.send()

    @api.model
    def send_email_invoice_canceled_tgalbo(self):
        limit_date = timedelta(days=1)
        date_cancel = fields.Date.today()
        date_cancel = fields.Datetime.from_string(date_cancel)
        date_cancel = date_cancel - limit_date
        inv_ids = self.search([
            ('state', '=', ['cancel']),
            ('company_id', '=', 4),
            ('type', '=', 'out_invoice'),
            ('date_cancelled', '=', date_cancel)])
        table = ''
        remp_date = ''
        remp_rep = ''
        for inve in inv_ids:
            if not inve.date_cancelled:
                remp_date = '---'
            else:
                remp_date = inve.date_cancelled
            if not inve.invoice_replaced:
                remp_rep = '---'
            else:
                remp_rep = inve.invoice_replaced.number
            table += """
                <tr>
                    <td style="border-bottom: 1px solid silver; color: #000; font-size: 12px;">%s</td>
                    <td style="border-bottom: 1px solid silver; color: #000; font-size: 12px;">%s</td>
                    <td style="border-bottom: 1px solid silver; color: #000; font-size: 12px;">%s</td>
                    <td align="right" style="border-bottom: 1px solid silver; color: #000; font-size: 12px;">
                    %s</td>
                </tr>
            """ % (remp_date, inve.partner_id.name, inve.number_cancel, remp_rep)

        destinatarios = self.env['ir.config_parameter'].sudo().get_param('cancelled_invoices_galbo.receivers_email', 'False')
        mail_obj = self.env['mail.mail']
        body_mail = u"""
            <div summary="o_mail_notification" style="padding:0px; width:90%%;
             margin:0 auto; background: #FFFFFF repeat top /100%%; color:#777777">
                <table cellspacing="0" cellpadding="0" style="width:100%%;
                border-collapse:collapse;">
                    <tbody><tr>
                        <td valign="center" width="270" style="padding:5px 10px
                         5px 5px;font-size: 17px; font-family:'Arial';">
                            <b>Las siguientes facturas ya fueron canceladas</b>
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
                        <th width="17%%" style="background-color: #a24689; color: #fff; padding:5px 10px 5px 5px;font-size: 14px;
                        border-bottom: 10px solid silver; font-family:'Arial';"><strong>Fecha de Cancelacion</strong></th>
                        <th width="50%%" style="background-color: #a24689; color: #fff; padding:5px 10px 5px 5px;font-size: 14px;
                        border-bottom: 10px solid silver; font-family:'Arial';"><strong>Cliente</strong></th>
                        <th width="17%%" style="background-color: #a24689; color: #fff; padding:5px 10px 5px 5px;font-size: 14px;
                        border-bottom: 10px solid silver; font-family:'Arial';"><strong>Factura Cancelada</strong></th>
                        <th width="17%%" style="background-color: #a24689; color: #fff; padding:5px 10px 5px 5px;font-size: 14px;
                        border-bottom: 10px solid silver; font-family:'Arial';"><strong>Factura que Sustituye</strong></th>
                    </tr>
                    %s
                    </tbody>
                </table>
            </div>
          """ % (self.env.user.company_id.name, table)
        mail = mail_obj.create({
            'subject': 'Facturas Canceladas Transportes Galbo del Norte',
            'email_to': destinatarios,
            # 'soporte.odoo@gebesa.com,salmon@gebesa.com,contabilidad@tansportesgalbo.com,luis.cabrales@transportesgalbo.com',
            'headers': "{'Return-Path': u'odoo@gebesa.com'}",
            'body_html': body_mail,
            'auto_delete': True,
            'message_type': 'comment',
            'model': 'account.invoice',
            # 'res_id': inv_ids[0].id,
        })
        mail.send()
