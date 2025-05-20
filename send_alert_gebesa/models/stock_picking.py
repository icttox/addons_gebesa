# Copyright 2022, Marco Esquivel
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

# from datetime import date, timedelta
from odoo import api, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def _alert_picking_from_customer_location(self):
        self._cr.execute(
            """
            SELECT sp.name, sp.date_done,
            sp.origin, sp.adjustment_responsible, sp.adj_reason,
            sp.adj_class, sl.name,
            sld.name, sum(am.amount)
            FROM stock_picking as sp
            left JOIN stock_location as sl ON sl.id = sp.location_id
            left JOIN stock_location as sld ON sld.id = sp.location_dest_id
            left join account_move as am on am.ref = sp.name
            where sp.state = 'done'
            and sp.company_id = 1
            and sl.usage = 'customer'
            and sld.usage = 'internal'
            and sp.date_done between date_trunc('day', current_date) - interval '1 day' and date_trunc('day', current_date)
            group by sp.id,sl.id,sld.id
            order by date_done
            """,)
        if not self._cr.rowcount:
            return []
        return self._cr.fetchall()

    @api.model
    def send_alert_picking_from_customer_location(self):
        # yesterday = fields.Date.to_string(date.today() - timedelta(days=1))

        # locations = self.env['stock.location'].search(
            # [('usage', '=', 'customer')])

        # locations_dest = self.env['stock.location'].search(
            # [('usage', '=', 'internal')])

        # pickings = self.search([
            # ('date_done', '>=', yesterday),
            # ('date_done', '<', date.today()),
            # ('state', '=', 'done'),
            # ('company_id', '=', 1),
            # ('location_id', 'in', locations.ids),
            # ('location_dest_id', 'in', locations_dest.ids)])

        pickings = self._alert_picking_from_customer_location()
        table = ''

        if not pickings:
            return
        for picking in pickings:
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
                    <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">$ %s</td>
                </tr>
            """ % (
                picking[0], picking[1], picking[2], picking[3], picking[4], picking[5], picking[6], picking[7], '{:,.2f}'.format(picking[8]))

        body_mail = self.get_html_body_send_alert_picking_from_customer_location(table)
        destinatarios = self.env['ir.config_parameter'].sudo().get_param('send_alert.picking_from_customer_location', 'False')
        self.alert_picking_from_customer_location(body_mail, destinatarios)

    def get_html_body_send_alert_picking_from_customer_location(self, table=None):
        body_mail = u"""
            <div summary="o_mail_notification" style="padding:0px; width:90%%;
                margin:0 auto; background: #FFFFFF repeat top /100%%; color:#777777">
                <table cellspacing="0" cellpadding="0" style="width:100%%;
                border-collapse:collapse;">
                    <tbody><tr>
                        <td valign="center" width="270" style="padding:5px 10px
                         5px 5px;font-size: 17px; font-family:'Arial';">
                            <b>Alerta de Pickings desde customer location hacia ubicaciones de tipo interno del día anterior</b>
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
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Nombre picking</strong></th>
                        <th width="6%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Fecha efectiva</strong></th>
                        <th width="6%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Documento origen</strong></th>
                        <th width="6%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Responsable</strong></th>
                        <th width="6%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Razón</strong></th>
                        <th width="6%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Clasificación</strong></th>
                        <th width="6%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Ubicacion de origen</strong></th>
                        <th width="6%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Ubicacion destino</strong></th>
                        <th width="6%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Monto total</strong></th>
                    </tr>
                    %s
                    </tbody>
                </table>
            </div>
          """ % (self.env.user.company_id.name, table)
        return body_mail

    def alert_picking_from_customer_location(self, body_mail=None, destinatarios=None):
        mail = self.env['mail.mail'].create({
            'subject': 'Alerta de Pickings desde customer location hacia ubicaciones de tipo interno del día anterior',
            'email_to': destinatarios,
            'headers': "{'Return-Path': u'odoo@gebesa.com'}",
            'body_html': body_mail,
            'auto_delete': True,
            'message_type': 'comment',
        })
        mail.send()
