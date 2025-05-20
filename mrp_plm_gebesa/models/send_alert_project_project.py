from datetime import datetime
from odoo import models, api, fields
import numpy as np
import dateutil.parser


class ProjectProject(models.Model):
    _inherit = 'project.project'

    @api.model
    def send_email_projec_project(self):
        # day = fields.Datetime.to_string(datetime.today())

        stages = self.env['project.task.type'].search(
            [('name', '!=', 'FINALIZADO')])

        tasks_slopes = self.env['project.task'].search([
            ('stage_id', 'in', stages.ids)],
            order='create_date asc')

        table = ''

        for task in tasks_slopes:
            day = fields.Datetime.to_string(datetime.today())
            create_date = fields.Datetime.to_string(task.create_date)
            day_date = dateutil.parser.parse(day).date()
            create_date_date = dateutil.parser.parse(create_date).date()
            days_natural = day_date - create_date_date
            days_natural = days_natural.days
            dayss = np.busday_count(create_date_date, day_date)
            if dayss < 3:
                continue

            base_url = self.env['ir.config_parameter'].get_param('web.base.url')
            base_url += '/web#id=%s&view_type=form&model=%s' % (task.id, task._name)

            table += """
                <tr><td align="left" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                    <td align="left" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">
                    <a href="%s" target="_blank" style="text-decoration:none; color: #a24689; font-family:'Arial';">%s
                    </a>
                </td>
                    <td align="left" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                    <td align="left" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                    <td align="left" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                    <td align="left" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                    <td align="left" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                    <td align="left" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                </tr>
            """ % (
                task.project_id.name,
                base_url,
                task.name,
                task.product_id.name,
                task.partner_id.name,
                task.user_id.name,
                dayss,
                days_natural,
                task.create_date)

        body_mail = self.get_html_body_project_project(table)
        destinatarios = self.env['ir.config_parameter'].sudo().get_param('mrp_plm_gebesa.receivers_email', 'False')
        self.send_alert_project_project(body_mail, destinatarios)

    def get_html_body_project_project(self, table=None):
        body_mail = u"""
            <div summary="o_mail_notification" style="padding:0px; width:90%%;
                margin:0 auto; background: #FFFFFF repeat top /100%%; color:#777777">
                <table cellspacing="0" cellpadding="0" style="width:100%%;
                border-collapse:collapse;">
                    <tbody><tr>
                        <td valign="center" width="270" style="padding:5px 10px
                         5px 5px;font-size: 17px; font-family:'Arial';">
                            <b>Tareas fuera de tiempo</b>
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
                        <th width="10%%" align="left" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Proyecto</strong></th>
                        <th width="6%%" align="left" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Nombre</strong></th>
                        <th width="10%%" align="left" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Producto</strong></th>
                        <th width="7%%" align="left" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Cliente</strong></th>
                        <th width="7%%" align="left" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Usuario</strong></th>
                        <th width="6%%" align="left" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Dias laborables</strong></th>
                        <th width="6%%" align="left" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Dias naturales</strong></th>
                        <th width="6%%" align="left" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Fecha de la tarea</strong></th>
                    </tr>
                    %s
                    </tbody>
                </table>
            </div>
          """ % (self.env.user.company_id.name, table)
        return body_mail

    def send_alert_project_project(self, body_mail=None, destinatarios=None):
        mail = self.env['mail.mail'].create({
            'subject': 'Tareas fuera de tiempo',
            'email_to': destinatarios,
            'headers': "{'Return-Path': u'odoo@gebesa.com'}",
            'body_html': body_mail,
            'auto_delete': True,
            'message_type': 'comment',
        })
        mail.send()
