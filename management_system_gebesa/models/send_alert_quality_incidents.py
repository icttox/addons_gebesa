# Copyright 2022, Marco Esquivel
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from datetime import date, timedelta
from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = 'quality.incidents'

    @api.model
    def send_incidents(self):
        yesterday = fields.Date.to_string(date.today() - timedelta(days=1))

        incidents = self.search([
            ('create_date', '>=', yesterday),
            ('create_date', '<', date.today())])

        table = ''

        for incident in incidents:
            # incident_state = ''

            # if incident.replacement == 'product':
                # incident_state = 'Producto / Partes incorrectas'
            # if incident.replacement == 'hits':
                # incident_state = 'Golpes'
            # if incident.replacement == 'default':
                # incident_state = 'Defecto MP'
            # if incident.replacement == 'design':
                # incident_state = 'Diseño incorrecto'
            # if incident.replacement == 'error':
                # incident_state = 'Error en produccion'
            # if incident.replacement == 'merchandise_not_arrive':
                # incident_state = 'No llega la mercancia / Partes'
            # if incident.replacement == 'fault_purchased_product':
                # incident_state = 'Falla en producto de compra / venta'
            # if incident.replacement == 'release':
                # incident_state = 'Liberacion erronea'
            # if incident.replacement == 'incident_client':
                # incident_state = 'Incidencia por cliente'
            # if incident.replacement == 'welding':
                # incident_state = 'Soldadura'
            # if incident.replacement == 'painting':
                # incident_state = 'Pintura'
            # if incident.replacement == 'finishes':
                # incident_state = 'Acabados'
            # if incident.replacement == 'dirty':
                # incident_state = 'Sucio'
            # if incident.replacement == 'armed':
                # incident_state = 'Armado'
            # if incident.replacement == 'supplied_by_service':
                # incident_state = 'Se surte por servicio'
            # if incident.replacement == 'production_quality_error':
                # incident_state = 'Error de Producción/Calidad'
            # if incident.replacement == 'freight_loses_package':
                # incident_state = 'Fletera pierde paquete'
            # if incident.replacement == 'buy_and_sell':
                # incident_state = 'Compra/venta'
            # if incident.replacement == 'wrong_measurements':
                # incident_state = 'Medidas incorrectas'
            # if incident.replacement == 'lack_of_components':
                # incident_state = 'Falta de componentes'
            # if incident.replacement == 'shipments':
                # incident_state = 'Embarques'

            table += """
                <tr>
                    <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                    <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                    <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                    <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                    <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                    <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                    <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                    <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                    <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">$%s</td>
                    <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                </tr>
            """ % (
                str(incident.date_incident),
                str(incident.product_id.name),
                str(incident.amount),
                str(incident.replacement_id.name),
                str(incident.warehouse_id.name),
                str(incident.departament_id.name),
                str(incident.sale_order_id.name),
                str(incident.order_id.name),
                '{:,.2f}'.format(incident.net_sale_mx),
                str(incident.create_uid.name))

        body_mail = self.get_html_body_incidents(table)
        destinatarios = self.env['ir.config_parameter'].sudo().get_param('send_alert_incidents.receivers_email', 'False')
        self.send_alert_incident(body_mail, destinatarios)

    def get_html_body_incidents(self, table=None, partner=False):
        if not partner:
            partner = self.env.user.partner_id
        body_mail = u"""
            <div summary="o_mail_notification" style="padding:0px; width:90%%;
                margin:0 auto; background: #FFFFFF repeat top /100%%; color:#777777">
                <table cellspacing="0" cellpadding="0" style="width:100%%;
                border-collapse:collapse;">
                    <tbody><tr>
                        <td valign="center" width="270" style="padding:5px 10px
                         5px 5px;font-size: 17px; font-family:'Arial';">
                            <b>Incidencias</b>
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
                    <tbody>
                    <tr>
                        <th width="10%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Fecha de incidencia</strong></th>
                        <th width="6%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Nombre del producto</strong></th>
                        <th width="6%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Cantidad</strong></th>
                        <th width="6%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Motivo de reposicion</strong></th>
                        <th width="6%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Almacen</strong></th>
                        <th width="6%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Departamento</strong></th>
                        <th width="7%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Pedido de origen</strong></th>
                        <th width="6%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Pedido actual</strong></th>
                        <th width="6%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Venta neta(pesos)</strong></th>
                        <th width="6%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Creador de incidencia</strong></th>
                    </tr>
                    %s
                    </tbody>
                </table>
            </div>
          """ % (self.env.user.partner_id.name, table)
        return body_mail

    def send_alert_incident(self, body_mail=None, destinatarios=None):
        mail = self.env['mail.mail'].create({
            'subject': 'Alerta de incidencias del dia de ayer',
            'email_to': destinatarios,
            'headers': "{'Return-Path': u'odoo@gebesa.com'}",
            'body_html': body_mail,
            'auto_delete': True,
            'message_type': 'comment',
        })
        mail.send()
