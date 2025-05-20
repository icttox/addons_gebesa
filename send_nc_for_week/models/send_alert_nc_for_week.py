
from datetime import datetime
from odoo import fields, models, api


class SendAlertNcForWeek(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def send_email_nc_alert_for_week_m(self):
        acoun = self.search([('type', '=', 'out_refund'),
                            ('state', 'not in', ['draft', 'cancel'])])
        day_day = datetime.today()
        table = ''
        for date in acoun:
            limit_date = date.date_invoice
            days = day_day - fields.Datetime.from_string(limit_date)
            days = days.days
            date_state = date.state.encode('utf8')
            busquedafacturapadre = self.search([('number', '=', date.origin)])
            if date.state == 'paid':
                date_state = 'pagado'
            if date.state == 'open':
                date_state = 'abierto'
            if busquedafacturapadre:
                for busfactupadre in busquedafacturapadre:
                    total_fact_padre = busfactupadre.amount_total
                    fecha_fact_padre = busfactupadre.date_invoice
                if days <= 7:
                    table += """
                        <tr><td style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                            <td style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                            <td style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                            <td style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                            <td style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                            <td style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                            <td style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                            <td style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                            <td style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                            <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                        </tr>
                    """ % (date.partner_id.name, limit_date, date.number, date.amount_total, date.refund_reason, fecha_fact_padre, date.origin, total_fact_padre, date.residual, date_state)
        mail_obj = self.env['mail.mail']
        body_mail = u"""
            <div summary="o_mail_notification" style="padding:0px; width:90%%;
             margin:0 auto; background: #FFFFFF repeat top /100%%; color:#777777">
                <table cellspacing="0" cellpadding="0" style="width:100%%;
                border-collapse:collapse;">
                    <tbody><tr>
                        <td valign="center" width="270" style="padding:5px 10px
                         5px 5px;font-size: 17px; font-family:'Arial';">
                            <b>Notas de credito semana anterior</b>
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
                        <th width="15%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial'; 
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>
                        Cliente</strong></th>
                        <th width="15%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial'; 
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>
                        Fecha NC</strong></th>
                        <th width="16%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial'; 
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>
                        Folio NC</strong></th>
                        <th width="15%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial'; 
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>
                        Total NC</strong></th>
                        <th width="15%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial'; 
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>
                        Motivo</strong></th>
                        <th width="15%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial'; 
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>
                        Fecha factura </strong></th>
                        <th width="15%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial'; 
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>
                        Factura Original</strong></th>
                        <th width="15%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial'; 
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>
                        Total factura </strong></th>
                        <th width="15%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial'; 
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>
                        Saldo Pendiente</strong></th>
                        <th width="15%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial'; 
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>
                        Estado NC</strong></th>

                    </tr>
                    %s
                    </tbody>
                </table>
            </div>
          """ % (self.env.user.company_id.name, table)
        destinatarios = self.env['ir.config_parameter'].sudo().get_param('send_nc_for_week.receivers_email', 'False')
        mail = mail_obj.create({
            'subject': 'Notas de credito de la semana pasada',
            'email_to': destinatarios,
            # 'email_to': 'salmon@gebesa.com,cesar.barron@gebesa.com,deysy.mascorro@gebesa.com,samuel.barron@gebesa.com',
            'headers': "{'Return-Path': u'odoo@gebesa.com'}",
            'body_html': body_mail,
            'auto_delete': True,
            'message_type': 'comment',
        })
        mail.send()
