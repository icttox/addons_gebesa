# Copyright 2022, Marco Esquivel
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class SendAlertFuelVouchers(models.Model):
    _inherit = 'fleet.vehicle.log.fuel'

    def _data_send_alert_fuel_vouchers(self):
        self._cr.execute(
            """
            SELECT fvlf.name AS nombre_vale,
            round(cast(fvlf.price_total AS numeric), 2) total_vale,
            REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(fvlf.state, 'draft', 'Borrador'), 'approved', 'Aprovado'), 'confirmed', 'Confirmado'), 'closed', 'Cerado'), 'cancel', 'Cancelado') AS status,
            sp.name AS nombre_albaran,
            round(am.amount,2) AS total_albaran
            FROM fleet_vehicle_log_fuel AS fvlf
            LEFT JOIN stock_picking AS sp ON fvlf.picking_id = sp.id
            LEFT JOIN account_move am ON sp.name = am.ref
            WHERE round(cast(fvlf.price_total AS numeric), 2) <> round(am.amount,2)
            AND date(fvlf.create_date) = CURRENT_DATE - INTERVAL '1 DAY'
            ORDER BY fvlf.name
            """,)
        if not self._cr.rowcount:
            return []
        return self._cr.fetchall()

    @api.model
    def send_alert_fuel_vouchers(self):
        vauchers = self._data_send_alert_fuel_vouchers()
        table = ''

        if not vauchers:
            return
        for vaucher in vauchers:
            table += """
                <tr>
                    <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                    <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">$ %s</td>
                    <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                    <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                    <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">$ %s</td>
                </tr>
            """ % (
                vaucher[0], '{:,.2f}'.format(vaucher[1]), vaucher[2], vaucher[3], '{:,.2f}'.format(vaucher[4]))

        body_mail = self.get_html_body_send_alert_fuel_vauchers(table)
        destinatarios = self.env['ir.config_parameter'].sudo().get_param('send_alert.fuel_vauchers', 'False')
        self.alert_fuel_vauchers(body_mail, destinatarios)

    def get_html_body_send_alert_fuel_vauchers(self, table=None):
        body_mail = u"""
            <div summary="o_mail_notification" style="padding:0px; width:90%%;
                margin:0 auto; background: #FFFFFF repeat top /100%%; color:#777777">
                <table cellspacing="0" cellpadding="0" style="width:100%%;
                border-collapse:collapse;">
                    <tbody><tr>
                        <td valign="center" width="270" style="padding:5px 10px
                         5px 5px;font-size: 17px; font-family:'Arial';">
                            <b>Alerta de vales de combustible de un dia anterior que no tienen el mismo total que su albaran</b>
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
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Numero de vale</strong></th>
                        <th width="10%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Total vale</strong></th>
                        <th width="6%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Status vale</strong></th>
                        <th width="6%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Nombre albaran</strong></th>
                        <th width="6%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Total albaran</strong></th>
                    </tr>
                    %s
                    </tbody>
                </table>
            </div>
          """ % (self.env.user.company_id.name, table)
        return body_mail

    def alert_fuel_vauchers(self, body_mail=None, destinatarios=None):
        mail = self.env['mail.mail'].create({
            'subject': 'Alerta de vales de combustible',
            'email_to': destinatarios,
            'headers': "{'Return-Path': u'odoo@gebesa.com'}",
            'body_html': body_mail,
            'auto_delete': True,
            'message_type': 'comment',
        })
        mail.send()
