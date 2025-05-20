
from datetime import date, timedelta
from odoo import fields, models, api


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.model
    def send_alert_payment(self):
        # import ipdb; ipdb.set_trace()
        yesterday = fields.Date.to_string(date.today() - timedelta(days=1))

        pagos = self.search([
            ('payment_type', '=', 'inbound'),
            ('state', 'not in', ['draft', 'cancelled']),
            ('create_date', '>=', yesterday),
            ('create_date', '<', date.today()),
            ('l10n_mx_edi_pac_status', '=', 'to_sign')])

        companys = pagos.mapped('company_id')
        # destinos = {1: 'credicobranza@gebesa.com,pedro.acosta@gebesa.com',
        #             3: 'secia.dominguez@gebesa.com,abril.romero@gebesa.com,pedro.acosta@gebesa.com',
        #             4: 'luis.cabrales@transportesgalbo.com,contabilidad@transportesgalbo.com',
        #             9: 'javier.labastida@gebesa.com'}
        # destdefault = 'cesar.barron@gebesa.com,marco.esquivel@gebesa.com,deysy.mascorro@gebesa.com,samuel.barron@gebesa.com,'

        for comp in companys:
            destinatarios = self.env['ir.config_parameter'].sudo().get_param('send_alert_payments.receivers_email_dest_company_' + str(comp.id), 'False')
            table = ''
            for reco in pagos.filtered(lambda py: py.company_id == comp):
                reco_state = ''

                if reco.l10n_mx_edi_pac_status == 'to_sign':
                    reco_state = 'Para Timbrar'

                table += """
                    <tr><td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                        <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                        <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                        <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">$%s</td>
                        <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                    </tr>
                """ % (
                    reco.create_date, reco.name, reco.partner_id.name,
                    '{:,.2f}'.format(reco.amount), reco_state)

            body_mail = self.get_html_body(table)
            # destinatarios = destdefault
            # if comp.id in destinos:
            #     destinatarios = destinatarios + destinos[comp.id]
            titulo = 'Pagos no timbrados de cliente: Empresa ' + comp.name
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
                            <b>Pagos no timbrados del cliente del dia de ayer</b>
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
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Fecha del Pago</strong></th>
                        <th width="6%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Folio del Pago</strong></th>
                        <th width="7%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Socio</strong></th>
                        <th width="6%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Monto Pagado</strong></th>
                        <th width="12%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Estado del PAC</strong></th>
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
