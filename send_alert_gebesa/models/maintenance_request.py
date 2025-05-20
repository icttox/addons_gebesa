# Copyright 2022, Marco Esquivel
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from odoo import models, api
from datetime import datetime, timedelta


class SendAlertMaintenanceRequest(models.Model):
    _inherit = 'maintenance.request'

    @api.model
    def send_email_maintenance_request(self):

        three_days = datetime.now().date() - timedelta(days=3)
        maintenances = self.sudo().search([
            ('stage_id', 'in', [1, 2]),
            ('maintenance_team_id', '=', 2),
            ('request_date', '<', three_days)])

        if not maintenances:
            return

        table = ''
        for maintenance in maintenances:
            days_in_status = (datetime.now().date() - maintenance.request_date).days
            attended_names = ', '.join(maintenance.attended_ids.mapped('name'))
            table += """
                <tr style="font-size: 12px; font-family:'Arial';">
                    <td align="center" style="border-bottom: 1px solid silver; color: #000;">%s</td>
                    <td align="center" style="border-bottom: 1px solid silver; color: #000;">%s</td>
                    <td align="center" style="border-bottom: 1px solid silver; color: #000;">%s</td>
                    <td align="center" style="border-bottom: 1px solid silver; color: #000;">%s</td>
                    <td align="center" style="border-bottom: 1px solid silver; color: #000;">%s</td>
                    <td align="center" style="border-bottom: 1px solid silver; color: #000;">%s</td>
                    <td align="center" style="border-bottom: 1px solid silver; color: #000;">%s</td>
                    <td align="center" style="border-bottom: 1px solid silver; color: #000;">%s</td>
                    <td align="center" style="border-bottom: 1px solid silver; color: #000;">%s</td>
                    <td align="center" style="border-bottom: 1px solid silver; color: #000;">%s</td>
                    <td align="center" style="border-bottom: 1px solid silver; color: #000;">%s</td>
                </tr>
            """ % (
                maintenance.name, maintenance.request_date, maintenance.employee_id.name,
                maintenance.equipment_id.name, maintenance.location_physical.name, maintenance.description,
                maintenance.technical_description, maintenance.maintenance_type, maintenance.stage_id.name,
                attended_names, days_in_status)

        body_mail = self.get_html_body_maintenance_request(table)
        destinatarios = self.env['ir.config_parameter'].sudo().get_param('send_alert.maintenace_request', 'False')
        self.send_alert_maintenance_request(body_mail, destinatarios)

    def get_html_body_maintenance_request(self, table=None):
        body_mail = u"""
            <div summary="o_mail_notification" style="padding:0px; width:90%%;
             margin:0 auto; background: #FFFFFF repeat top /100%%; color:#777777">
                <table cellspacing="0" cellpadding="0" style="width:100%%;
                border-collapse:collapse;">
                    <tbody><tr>
                        <td valign="center" width="270" style="padding:5px 10px
                         5px 5px;font-size: 17px; font-family:'Arial';">
                            <b>Peticiones de mantenimiento mayores a 3 dias</b>
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
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Folio</strong></th>
                        <th width="10%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Fecha de solicitud</strong></th>
                        <th width="10%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Creador</strong></th>
                        <th width="6%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Activo</strong></th>
                        <th width="6%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Ubicacion fisica</strong></th>
                        <th width="6%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Descripcion</strong></th>
                        <th width="6%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Descripcion tecnica</strong></th>
                        <th width="6%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Tipo mantenimiento</strong></th>
                        <th width="6%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Status</strong></th>
                        <th width="6%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Atendio</strong></th>
                        <th width="6%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Dias transcurridos</strong></th>
                    </tr>
                    %s
                    </tbody>
                </table>
            </div>
          """ % (self.env.user.company_id.name, table)
        return body_mail

    def send_alert_maintenance_request(self, body_mail=None, destinatarios=None, titulo=None):
        mail = self.env['mail.mail'].create({
            'subject': 'Alerta de peticiones de mantenimiento',
            'email_to': destinatarios,
            'headers': "{'Return-Path': u'odoo@gebesa.com'}",
            'body_html': body_mail,
            'auto_delete': True,
            'message_type': 'comment',
        })
        mail.send()
