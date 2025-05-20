
from datetime import date, timedelta
from odoo import fields, models, api


class SendAlertNc(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def send_email_nc_alert_m(self):

        yesterday = fields.Date.to_string(date.today() - timedelta(days=1))

        notas = self.search([
            ('type', '=', 'out_refund'),
            ('state', 'not in', ['draft', 'cancel']),
            ('date_invoice', '=', yesterday)])

        companies = notas.mapped('company_id')
        # destinos = {1: 'esmeralda.gutierrez@gebesa.com,credicobranza@gebesa.com,pedro.acosta@gebesa.com,boyardo@gebesa.com',
        #             3: 'secia.dominguez@gebesa.com,abril.romero@gebesa.com,pedro.acosta@gebesa.com,georgina.salmon@gebesa.com',
        #             10: 'pedro.acosta@gebesa.com,abril.romero@gebesa.com,credicobranza@gebesa.com',
        #             4: 'luis.cabrales@transportesgalbo.com,contabilidad@transportesgalbo.com'}
        # destdefault = 'salmon@gebesa.com,cesar.barron@gebesa.com,deysy.mascorro@gebesa.com,samuel.barron@gebesa.com,'

        for comp in companies:

            destinatarios = self.env['ir.config_parameter'].sudo().get_param('send_alert_nc.receivers_email_dest_company_' + str(comp.id), 'False')

            table = ''
            for reco in notas.filtered(lambda nc: nc.company_id == comp):
                reco_state = ''
                origen = self.search([('number', '=', reco.origin)], limit=1)

                total_origen = origen.amount_total if origen else 0
                fecha_origen = origen.date_invoice if origen else ''

                if reco.state == 'paid':
                    reco_state = 'pagado'
                if reco.state == 'open':
                    reco_state = 'abierto'

                table += """
                    <tr><td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                        <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                        <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                        <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">$%s</td>
                        <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                        <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                        <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                        <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">$%s</td>
                        <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">$%s</td>
                        <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                    </tr>
                """ % (
                    reco.partner_id.name, reco.date_invoice, reco.number,
                    '{:,.2f}'.format(reco.amount_total), reco.name, fecha_origen,
                    reco.origin, '{:,.2f}'.format(total_origen), '{:,.2f}'.format(reco.residual), reco_state)

            body_mail = self.get_html_body(table)
            # destinatarios = destdefault + destinos[comp.id]
            titulo = 'Notas de credito de el dia de ayer Empresa: ' + comp.name
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
                            <b>Notas de credito</b>
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
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Fecha NC</strong></th>
                        <th width="7%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Folio NC</strong></th>
                        <th width="6%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Total NC</strong></th>
                        <th width="12%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Motivo</strong></th>
                        <th width="6%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Fecha factura </strong></th>
                        <th width="7%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Factura Original</strong></th>
                        <th width="6%%" style="padding:5px 10px 8px 8px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Total factura </strong></th>
                        <th width="5%%" style="padding:8px 10px 8px 8px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Saldo Pendiente</strong></th>
                        <th width="6%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Estado NC</strong></th>
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
