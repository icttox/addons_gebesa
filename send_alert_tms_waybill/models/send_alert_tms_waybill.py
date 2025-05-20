from datetime import datetime
from odoo import fields, models, api


class TmsWaybill(models.Model):
    _inherit = 'tms.waybill'

    @api.model
    def send_email_tms_waybill(self):
        waybills = self.search([('state', '=', 'cancel')])
        now = datetime.today()
        table = ''
        for waybill in waybills:
            if waybill.date_cancell:
                limit_date = waybill.date_cancell
                days = now - fields.Datetime.from_string(limit_date)
                days = days.days
                # if waybill.state == 'cancel':
                # waybill_state = 'cancelada'
                if days <= 1:
                    table += """
                        <tr><td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                            <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                            <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                            <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">$ %s</td>
                            <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                            <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                        </tr>
                    """ % (waybill.date_order, waybill.name, waybill.partner_id.name, '{:,.2f}'.format(waybill.amount_total), waybill.motivo_cancel, waybill.date_cancell)
        mail_obj = self.env['mail.mail']
        body_mail = u"""
                            <div summary="o_mail_notification" style="padding:0px; width:90%%;
             margin:0 auto; background: #FFFFFF repeat top /100%%; color:#777777">
                <table cellspacing="0" cellpadding="0" style="width:100%%;
                border-collapse:collapse;">
                    <tbody><tr>
                        <td valign="center" width="270" style="padding:5px 10px
                         5px 5px;font-size: 17px; font-family:'Arial';">
                            <b>Cartas Porte Canceladas</b>
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
                        <th width="15%%" style="background-color: #a24689; color: #fff; padding:5px 10px 5px 5px;font-size: 14px;
                        border-bottom: 10px solid silver; font-family:'Arial';">
                        Fecha CP</strong></th>
                        <th width="15%%" style="background-color: #a24689; color: #fff; padding:5px 10px 5px 5px;font-size: 14px;
                        border-bottom: 10px solid silver; font-family:'Arial';">
                        Folio CP Cancelada</strong></th>
                        <th width="20%%" style="background-color: #a24689; color: #fff; padding:5px 10px 5px 5px;font-size: 14px;
                        border-bottom: 10px solid silver; font-family:'Arial';">
                        Cliente</strong></th>
                        <th width="15%%" style="background-color: #a24689; color: #fff; padding:5px 10px 5px 5px;font-size: 14px;
                        border-bottom: 10px solid silver; font-family:'Arial';">
                        Total</strong></th>
                        <th width="20%%" style="background-color: #a24689; color: #fff; padding:5px 10px 5px 5px;font-size: 14px;
                        border-bottom: 10px solid silver; font-family:'Arial';">
                        Motivo de Cancelacion</strong></th>
                        <th width="15%%" style="background-color: #a24689; color: #fff; padding:5px 10px 5px 5px;font-size: 14px;
                        border-bottom: 10px solid silver; font-family:'Arial';">
                        Fecha de Cancelacion</strong></th>
                    </tr>
                    %s
                    </tbody>
                </table>
            </div>
          """ % (self.env.user.company_id.name, table)
        destinatarios = self.env['ir.config_parameter'].sudo().get_param('send_alert_tms_waybill.receivers_email', 'False')
        mail = mail_obj.create({
            'subject': 'Cartas Porte Canceladas',
            'email_to': destinatarios,
            # 'email_to': 'salmon@gebesa.com,cesar.barron@gebesa.com,deysy.mascorro@gebesa.com,samuel.barron@gebesa.com,luis.cabrales@transportesgalbo.com',
            'headers': "{'Return-Path': u'odoo@gebesa.com'}",
            'body_html': body_mail,
            'auto_delete': False,
            'message_type': 'comment',
        })
        mail.send()
