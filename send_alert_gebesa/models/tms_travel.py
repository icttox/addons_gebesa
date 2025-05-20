# Copyright 2022, Marco Esquivel
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import models, api


class SendAlertMissingCpPartnersInvoicesGalbo(models.Model):
    _inherit = 'tms.travel'

    @api.model
    def send_email_missing_cp_partners_invoices_galbo(self):

        travels = self.sudo().search([
            ('state', 'in', ['draft', 'progress'])])

        partners = travels.mapped('partner_id')
        destinatarios = self.env['ir.config_parameter'].sudo().get_param('send_alert_invoices.missing_cp_partners_invoices_galbo', 'False')
        table = ''
        for partner in partners:
            if not partner.zip:
                table += """
                    <tr><td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                        <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                    </tr>
                """ % (
                    partner.name, partner.vat)

        body_mail = self.get_html_body(table)
        titulo = 'Codigo postal faltante del partner para facturar con 4.0 de la Empresa: Transportes Galbo Del Norte S.A. de C.V.' 
        self.send_alert(body_mail, destinatarios, titulo)

    def get_html_body(self, table=None):
        body_mail = u"""
            <div summary="o_mail_notification" style="padding:0px; width:90%%;
             margin:0 auto; background: #FFFFFF repeat top /100%%; color:#777777">
                <table cellspacing="0" cellpadding="0" style="width:100%%;
                border-collapse:collapse;">
                    <tbody><tr>
                        <td valign="center" width="270" style="padding:5px 10px
                         5px 5px;font-size: 17px; font-family:'Arial';">
                            <b>Codigo postal faltante del partner para facturar con 4.0</b>
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
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Nombre partner</strong></th>
                        <th width="6%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Rfc</strong></th>
                    </tr>
                    %s
                    </tbody>
                </table>
            </div>
          """ % (self.env.user.company_id.name, table)
        return body_mail

    def send_alert(self, body_mail=None, destinatarios=None, titulo=None):
        mail = self.env['mail.mail'].create({
            'subject': titulo,
            'email_to': destinatarios,
            'headers': "{'Return-Path': u'odoo@gebesa.com'}",
            'body_html': body_mail,
            'auto_delete': True,
            'message_type': 'comment',
        })
        mail.send()
