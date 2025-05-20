from datetime import datetime
from odoo import models, api


class SendAlertTravelMg(models.Model):
    _inherit = 'tms.travel'
    _order = 'partner_id, name asc'

    @api.model
    def send_email_travel_mg_m(self, email_to=False):
        today = datetime.today()
        date_init = str(today.year) + '-' + str(today.month) + '-' + str(today.day - 1)
        date_fin = str(today.year) + '-' + str(today.month) + '-' + str(today.day)
        expense_ids = self.env['tms.expense'].search([
            ('date_confirmed', '>=', date_init),
            ('date_confirmed', '<', date_fin)])

        travel_ids = self.search([
            ('state', '!=', 'cancel'),
            ('expense_id', 'in', expense_ids.ids)])

        table1 = ''
        table2 = ''
        table3 = ''
        footer1 = ''
        footer2 = ''
        footer3 = ''
        sum_costo_estimado_t1 = 0
        sum_costo_liquidar_t1 = 0
        sum_ingreso_operacion_t1 = 0
        margen_estimado_t1 = 0
        margen_total_t1 = 0
        sum_amount_salary_t1 = 0
        sum_amount_total_total_t1 = 0

        sum_costo_estimado_t2 = 0
        sum_costo_liquidar_t2 = 0
        sum_ingreso_operacion_t2 = 0
        margen_estimado_t2 = 0
        margen_total_t2 = 0
        sum_amount_salary_t2 = 0
        sum_amount_total_total_t2 = 0

        sum_costo_estimado_t3 = 0
        sum_costo_liquidar_t3 = 0
        sum_ingreso_operacion_t3 = 0
        margen_estimado_t3 = 0
        margen_total_t3 = 0
        sum_amount_salary_t3 = 0
        sum_amount_total_total_t3 = 0

        for travel in travel_ids:
            if travel.state == 'closed':
                date_state = 'cerrado'
                if travel.margen_final <= 48:
                    table1 += """

                    <div>
                        <style type="text/css">
                            tr {
                            font-family: 'Arial';
                                color: #000000;
                            }
                            strong {
                                font-size: 14px;
                            }
                        </style>
                    </div>
                        <tr align="center"><td align="left" style="border-bottom: 1px solid silver; font-size:12px; font-family:'Arial';">%s</td>
                            <td style="border-bottom: 1px solid silver; font-size:12px; font-family:'Arial';">%s</td>
                            <td style="border-bottom: 1px solid silver; font-size:12px; font-family:'Arial';">%s</td>
                            <td align="left" style="border-bottom: 1px solid silver; font-size:12px; font-family:'Arial';">%s</td>
                            <td style="border-bottom: 1px solid silver; font-size:12px; font-family:'Arial';">%s</td>
                            <td style="border-bottom: 1px solid silver; font-size:12px; font-family:'Arial';">$ %s</td>
                            <td style="border-bottom: 1px solid silver; font-size:12px; font-family:'Arial';">%s %%</td>
                            <td bgcolor= "#F78181" style="border-bottom: 1px solid silver; font-size:12px; font-family:'Arial';">$ %s</td>
                            <td bgcolor= "#F78181" style="border-bottom: 1px solid silver; font-size:12px; font-family:'Arial';">%s %%</td>
                            <td style="border-bottom: 1px solid silver; font-size:12px; font-family:'Arial';">$ %s</td>
                            <td align="center" style="border-bottom: 1px solid silver; font-size:12px; font-family:'Arial';">%s</td>
                        </tr>
                    """ % (
                        travel.partner_id.name,
                        travel.name, travel.unit_id.name, travel.route_id.name,
                        travel.date,
                        # "%.*f" % (2, travel.estimated_total_cost),
                        # "%.*f" % (2, travel.margen_utilidad),
                        '{:,.2f}'.format(travel.estimated_total_cost_without_driver),
                        # "%.*f" % (2, travel.estimated_total_cost_without_driver),
                        "%.*f" % (2, travel.margen_utilidad_without_driver),
                        '{:,.2f}'.format(travel.final_total_cost_wo_driver),
                        "%.*f" % (2, travel.margen_final),
                        '{:,.2f}'.format(travel.ingreso_operacion),
                        date_state)
                    sum_costo_estimado_t1 += travel.estimated_total_cost_without_driver
                    sum_costo_liquidar_t1 += travel.final_total_cost_wo_driver
                    sum_ingreso_operacion_t1 += travel.ingreso_operacion
                    sum_amount_total_total_t1 += travel.expense_id.amount_total_total
                    sum_amount_salary_t1 += travel.expense_id.amount_salary
                    margen_total_t1 = 0
                    margen_estimado_t1 = 0

                    if sum_ingreso_operacion_t1 > 0:
                        margen_total_t1 = ((sum_ingreso_operacion_t1 - (sum_amount_total_total_t1 - sum_amount_salary_t1)) / sum_ingreso_operacion_t1) * 100
                        margen_estimado_t1 = ((sum_ingreso_operacion_t1 - sum_costo_estimado_t1) / sum_ingreso_operacion_t1) * 100
                    footer1 = u"""
                        <tr align="center"><td style="border-bottom: 1px solid silver; font-size:12px; font-family:'Arial';"></td>
                            <td style="border-bottom: 1px solid silver; font-size:12px; font-family:'Arial';"></td>
                            <td style="border-bottom: 1px solid silver; font-size:12px; font-family:'Arial';"></td>
                            <td style="border-bottom: 1px solid silver; font-size:12px; font-family:'Arial';"></td>
                            <td style="border-bottom: 1px solid silver; font-size:13px; font-family:'Arial'; font-weight: bold;"> TOTAL: </td>
                            <td style="border-bottom: 1px solid silver; font-weight: bold; font-size:13px; font-family:'Arial';">$ %s</td>
                            <td style="border-bottom: 1px solid silver; font-weight: bold; font-size:13px; font-family:'Arial';">%s %%</td>
                            <td bgcolor= "#F78181" style="border-bottom: 1px solid silver; font-weight: bold; font-size:13px; font-family:'Arial';">$ %s</td>
                            <td bgcolor= "#F78181" style="border-bottom: 1px solid silver; font-weight: bold; font-size:13px; font-family:'Arial';">%s %%</td>
                            <td style="border-bottom: 1px solid silver; font-size:13px; font-family:'Arial'; font-weight: bold;">$ %s</td>
                            <td align="center" style="border-bottom: 1px solid silver; font-size:12px; font-family:'Arial';"></td>
                        </tr>
                    """ % (
                        '{:,.2f}'.format(sum_costo_estimado_t1),
                        "%.*f" % (2, margen_estimado_t1),
                        '{:,.2f}'.format(sum_costo_liquidar_t1),
                        "%.*f" % (2, margen_total_t1),
                        '{:,.2f}'.format(sum_ingreso_operacion_t1))

                if travel.margen_final > 48 and travel.margen_final <= 54:
                    table2 += """

                    <div>
                        <style type="text/css">
                            tr {
                            font-family: 'Arial';
                                color: #000000;
                            }
                            strong {
                                font-size: 14px;
                            }
                        </style>
                    </div>
                        <tr align="center"><td align="left" style="border-bottom: 1px solid silver; font-size:12px; font-family:'Arial';">%s</td>
                            <td style="border-bottom: 1px solid silver; font-size:12px; font-family:'Arial';">%s</td>
                            <td style="border-bottom: 1px solid silver; font-size:12px; font-family:'Arial';">%s</td>
                            <td align="left" style="border-bottom: 1px solid silver; font-size:12px; font-family:'Arial';">%s</td>
                            <td style="border-bottom: 1px solid silver; font-size:12px; font-family:'Arial';">%s</td>
                            <td style="border-bottom: 1px solid silver; font-size:12px; font-family:'Arial';">$ %s</td>
                            <td style="border-bottom: 1px solid silver; font-size:12px; font-family:'Arial';">%s %%</td>
                            <td bgcolor= "#F78181" style="border-bottom: 1px solid silver; font-size:12px; font-family:'Arial';">$ %s</td>
                            <td bgcolor= "#F78181" style="border-bottom: 1px solid silver; font-size:12px; font-family:'Arial';">%s %%</td>
                            <td style="border-bottom: 1px solid silver; font-size:12px; font-family:'Arial';">$ %s</td>
                            <td align="center" style="border-bottom: 1px solid silver; font-size:12px; font-family:'Arial';">%s</td>
                        </tr>
                    """ % (
                        travel.partner_id.name,
                        travel.name, travel.unit_id.name, travel.route_id.name,
                        travel.date,
                        # "%.*f" % (2, travel.estimated_total_cost),
                        # "%.*f" % (2, travel.margen_utilidad),
                        '{:,.2f}'.format(travel.estimated_total_cost_without_driver),
                        # "%.*f" % (2, travel.estimated_total_cost_without_driver),
                        "%.*f" % (2, travel.margen_utilidad_without_driver),
                        '{:,.2f}'.format(travel.final_total_cost_wo_driver),
                        "%.*f" % (2, travel.margen_final),
                        '{:,.2f}'.format(travel.ingreso_operacion),
                        date_state)
                    sum_costo_estimado_t2 += travel.estimated_total_cost_without_driver
                    sum_costo_liquidar_t2 += travel.final_total_cost_wo_driver
                    sum_ingreso_operacion_t2 += travel.ingreso_operacion
                    sum_amount_total_total_t2 += travel.expense_id.amount_total_total
                    sum_amount_salary_t2 += travel.expense_id.amount_salary

                    margen_total_t2 = ((sum_ingreso_operacion_t2 - (sum_amount_total_total_t2 - sum_amount_salary_t2)) / sum_ingreso_operacion_t2) * 100
                    margen_estimado_t2 = ((sum_ingreso_operacion_t2 - sum_costo_estimado_t2) / sum_ingreso_operacion_t2) * 100
                    footer2 = u"""
                        <tr align="center"><td style="border-bottom: 1px solid silver; font-size:12px; font-family:'Arial';"></td>
                            <td style="border-bottom: 1px solid silver; font-size:12px; font-family:'Arial';"></td>
                            <td style="border-bottom: 1px solid silver; font-size:12px; font-family:'Arial';"></td>
                            <td style="border-bottom: 1px solid silver; font-size:12px; font-family:'Arial';"></td>
                            <td style="border-bottom: 1px solid silver; font-size:13px; font-family:'Arial'; font-weight: bold;"> TOTAL: </td>
                            <td style="border-bottom: 1px solid silver; font-weight: bold; font-size:13px; font-family:'Arial';">$ %s</td>
                            <td style="border-bottom: 1px solid silver; font-weight: bold; font-size:13px; font-family:'Arial';">%s %%</td>
                            <td bgcolor= "#F78181" style="border-bottom: 1px solid silver; font-weight: bold; font-size:13px; font-family:'Arial';">$ %s</td>
                            <td bgcolor= "#F78181" style="border-bottom: 1px solid silver; font-weight: bold; font-size:13px; font-family:'Arial';">%s %%</td>
                            <td style="border-bottom: 1px solid silver; font-size:13px; font-family:'Arial'; font-weight: bold;">$ %s</td>
                            <td align="center" style="border-bottom: 1px solid silver; font-size:12px; font-family:'Arial';"></td>
                        </tr>
                    """ % (
                        '{:,.2f}'.format(sum_costo_estimado_t2),
                        "%.*f" % (2, margen_estimado_t2),
                        '{:,.2f}'.format(sum_costo_liquidar_t2),
                        "%.*f" % (2, margen_total_t2),
                        '{:,.2f}'.format(sum_ingreso_operacion_t2))

                if travel.margen_final > 54:
                    table3 += """

                    <div>
                        <style type="text/css">
                            tr {
                            font-family: 'Arial';
                                color: #000000;
                            }
                            strong {
                                font-size: 14px;
                            }
                        </style>
                    </div>
                        <tr align="center"><td align="left" style="border-bottom: 1px solid silver; font-size:12px; font-family:'Arial';">%s</td>
                            <td style="border-bottom: 1px solid silver; font-size:12px; font-family:'Arial';">%s</td>
                            <td style="border-bottom: 1px solid silver; font-size:12px; font-family:'Arial';">%s</td>
                            <td align="left" style="border-bottom: 1px solid silver; font-size:12px; font-family:'Arial';">%s</td>
                            <td style="border-bottom: 1px solid silver; font-size:12px; font-family:'Arial';">%s</td>
                            <td style="border-bottom: 1px solid silver; font-size:12px; font-family:'Arial';">$ %s</td>
                            <td style="border-bottom: 1px solid silver; font-size:12px; font-family:'Arial';">%s %%</td>
                            <td bgcolor= "#F78181" style="border-bottom: 1px solid silver; font-size:12px; font-family:'Arial';">$ %s</td>
                            <td bgcolor= "#F78181" style="border-bottom: 1px solid silver; font-size:12px; font-family:'Arial';">%s %%</td>
                            <td style="border-bottom: 1px solid silver; font-size:12px; font-family:'Arial';">$ %s</td>
                            <td align="center" style="border-bottom: 1px solid silver; font-size:12px; font-family:'Arial';">%s</td>
                        </tr>
                    """ % (
                        travel.partner_id.name,
                        travel.name, travel.unit_id.name, travel.route_id.name,
                        travel.date,
                        # "%.*f" % (2, travel.estimated_total_cost),
                        # "%.*f" % (2, travel.margen_utilidad),
                        '{:,.2f}'.format(travel.estimated_total_cost_without_driver),
                        # "%.*f" % (2, travel.estimated_total_cost_without_driver),
                        "%.*f" % (2, travel.margen_utilidad_without_driver),
                        '{:,.2f}'.format(travel.final_total_cost_wo_driver),
                        "%.*f" % (2, travel.margen_final),
                        '{:,.2f}'.format(travel.ingreso_operacion),
                        date_state)
                    sum_costo_estimado_t3 += travel.estimated_total_cost_without_driver
                    sum_costo_liquidar_t3 += travel.final_total_cost_wo_driver
                    sum_ingreso_operacion_t3 += travel.ingreso_operacion
                    sum_amount_total_total_t3 += travel.expense_id.amount_total_total
                    sum_amount_salary_t3 += travel.expense_id.amount_salary

                    margen_total_t3 = ((sum_ingreso_operacion_t3 - (sum_amount_total_total_t3 - sum_amount_salary_t3)) / sum_ingreso_operacion_t3) * 100
                    margen_estimado_t3 = ((sum_ingreso_operacion_t3 - sum_costo_estimado_t3) / sum_ingreso_operacion_t3) * 100
                    footer3 = u"""
                        <tr align="center"><td style="border-bottom: 1px solid silver; font-size:12px; font-family:'Arial';"></td>
                            <td style="border-bottom: 1px solid silver; font-size:12px; font-family:'Arial';"></td>
                            <td style="border-bottom: 1px solid silver; font-size:12px; font-family:'Arial';"></td>
                            <td style="border-bottom: 1px solid silver; font-size:12px; font-family:'Arial';"></td>
                            <td style="border-bottom: 1px solid silver; font-size:13px; font-family:'Arial';" font-weight: bold;"> TOTAL: </td>
                            <td style="border-bottom: 1px solid silver; font-weight: bold; font-size:13px; font-family:'Arial';">$ %s</td>
                            <td style="border-bottom: 1px solid silver; font-weight: bold; font-size:13px; font-family:'Arial';">%s %%</td>
                            <td bgcolor= "#F78181" style="border-bottom: 1px solid silver; font-weight: bold; font-size:13px; font-family:'Arial';">$ %s</td>
                            <td bgcolor= "#F78181" style="border-bottom: 1px solid silver; font-weight: bold; font-size:13px; font-family:'Arial';">%s %%</td>
                            <td style="border-bottom: 1px solid silver; font-size:13px; font-weight: bold; font-family:'Arial';">$ %s</td>
                            <td align="center" style="border-bottom: 1px solid silver; font-size:12px; font-family:'Arial';"></td>
                        </tr>
                    """ % (
                        '{:,.2f}'.format(sum_costo_estimado_t3),
                        "%.*f" % (2, margen_estimado_t3),
                        '{:,.2f}'.format(sum_costo_liquidar_t3),
                        "%.*f" % (2, margen_total_t3),
                        '{:,.2f}'.format(sum_ingreso_operacion_t3))

        mail_obj = self.env['mail.mail']
        body_mail = u"""
                            <div summary="o_mail_notification" style="padding:0px; width:100%%;
                             margin:0 auto; background: #FFFFFF repeat top /100%%; color:#777777">
                                <table cellspacing="0" cellpadding="0" style="width:100%%;
                                border-collapse:collapse; background:inherit; color:inherit">
                                    <tbody><tr>
                                        <td valign="center" width="270" style="padding:5px 10px
                                         5px 5px;font-size: 18px; font-family:'Arial'; font_weight:"bold";">
                                            <p>Viajes liquidados de ayer</p>
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
                                        <td valign="top" style="width:900px; padding:5px 10px
                                        5px 5px; ">
                                            <div>
                                                <hr width="100%%" style="background-color:
                                                rgb(204,204,204);border:medium none;clear:both;
                                                display:block;font-size:0px;min-height:1px;
                                                line-height:0;margin:15px auto;padding:0">
                                            </div>
                                        </td>
                                    </tr></tbody>
                                </table>
                            </div>
                            <div style="padding:0px; width:100%%; margin:0 auto; background:
                            #FFFFFF repeat top /100%%;color:#777777">
                                <table style="border-collapse:collapse; margin: 0 auto; width:
                                100%%; background:inherit; color:inherit">
                                    <tbody>
                                    <tr>
                                        <h2 style="font-size:18px; font-family:'Arial'; color: #a24689;">
                                            Margen Bajo <b style="font-size:16px;">(menor a 48%%)</b>
                                        </h2>
                                    </tr>
                                    <tr>
                                        <th width="15%%" style="background-color: #a24689; color: #fff; padding:5px 10px 5px 5px;font-size: 12px; font-family:'Arial';
                                        border-bottom: 10px solid silver;"><strong>Cliente</strong></th>
                                        <th width="15%%" style="background-color: #a24689; color: #fff; padding:5px 10px 5px 5px;font-size: 12px; font-family:'Arial';
                                        border-bottom: 10px solid silver;"><strong>Num de Viaje</strong></th>
                                        <th width="15%%" style="background-color: #a24689; color: #fff; padding:5px 10px 5px 5px;font-size: 12px; font-family:'Arial';
                                        border-bottom: 10px solid silver;"><strong>Unidad</strong></th>
                                        <th width="15%%" style="background-color: #a24689; color: #fff; padding:5px 10px 5px 5px;font-size: 12px; font-family:'Arial';
                                        border-bottom: 10px solid silver;"><strong>Ruta</strong></th>
                                        <th width="15%%" style="background-color: #a24689; color: #fff; padding:5px 10px 5px 5px;font-size: 12px; font-family:'Arial';
                                        border-bottom: 10px solid silver;"><strong>Fecha</strong></th>
                                        <th width="15%%" style="background-color: #a24689; color: #fff; padding:5px 10px 5px 5px;font-size: 12px; font-family:'Arial';
                                        border-bottom: 10px solid silver;"><strong>Costo total estimado s/conductor</strong></th>
                                        <th width="15%%" style="background-color: #a24689; color: #fff; padding:5px 10px 5px 5px;font-size: 12px; font-family:'Arial';
                                        border-bottom: 10px solid silver;"><strong>Margen Estimado s/conductor</strong></th>
                                        <th width="15%%" style="background-color: #a24689; color: #fff; padding:5px 10px 5px 5px;font-size: 12px;  font-family:'Arial';
                                        border-bottom: 10px solid silver;"><strong>Costo al liquidar s/conductor</strong></th>
                                        <th width="15%%" style="background-color: #a24689; color: #fff; padding:5px 10px 5px 5px;font-size: 12px; font-family:'Arial';
                                        border-bottom: 10px solid silver;"><strong>Margen final s/conductor</strong></th>
                                        <th width="15%%" style="background-color: #a24689; color: #fff; padding:5px 10px 5px 5px;font-size: 12px; font-family:'Arial';
                                        border-bottom: 10px solid silver;"><strong>Ingreso Operacion</strong></th>
                                        <th width="15%%" style="background-color: #a24689; color: #fff; padding:5px 10px 5px 5px;font-size: 12px; font-family:'Arial';
                                        border-bottom: 10px solid silver;"><strong>Estado </strong></th>
                                    </tr>
                                    %s
                                    <br/>
                                    %s
                                    </tbody>
                                </table>
                                <br/><br/>
                                <table style="border-collapse:collapse; margin: 0 auto; width:
                                100%%; background:inherit; color:inherit">
                                    <tbody>
                                    <tr>
                                        <h2 style="font-size:18px; font-family:'Arial'; color: #a24689;">
                                            Margen Normal <b style="font-size:16px;">(entre 48%% y 54%%)</b>
                                        </h2>
                                    </tr>
                                    <tr>
                                        <th width="15%%" style="background-color: #a24689; color: #fff; padding:5px 10px 5px 5px;font-size: 12px; font-family:'Arial';
                                        border-bottom: 10px solid silver;"><strong>Cliente</strong></th>
                                        <th width="15%%" style="background-color: #a24689; color: #fff; padding:5px 10px 5px 5px;font-size: 12px; font-family:'Arial';
                                        border-bottom: 10px solid silver;"><strong>Num de Viaje</strong></th>
                                        <th width="15%%" style="background-color: #a24689; color: #fff; padding:5px 10px 5px 5px;font-size: 12px; font-family:'Arial';
                                        border-bottom: 10px solid silver;"><strong>Unidad</strong></th>
                                        <th width="15%%" style="background-color: #a24689; color: #fff; padding:5px 10px 5px 5px;font-size: 12px; font-family:'Arial';
                                        border-bottom: 10px solid silver;"><strong>Ruta</strong></th>
                                        <th width="15%%" style="background-color: #a24689; color: #fff; padding:5px 10px 5px 5px;font-size: 12px; font-family:'Arial';
                                        border-bottom: 10px solid silver;"><strong>Fecha</strong></th>
                                        <th width="15%%" style="background-color: #a24689; color: #fff; padding:5px 10px 5px 5px;font-size: 12px; font-family:'Arial';
                                        border-bottom: 10px solid silver;"><strong>Costo total estimado s/conductor</strong></th>
                                        <th width="15%%" style="background-color: #a24689; color: #fff; padding:5px 10px 5px 5px;font-size: 12px; font-family:'Arial';
                                        border-bottom: 10px solid silver;"><strong>Margen Estimado s/conductor</strong></th>
                                        <th width="15%%" style="background-color: #a24689; color: #fff; padding:5px 10px 5px 5px;font-size: 12px; font-family:'Arial';
                                        border-bottom: 10px solid silver;"><strong>Costo al liquidar s/conductor</strong></th>
                                        <th width="15%%" style="background-color: #a24689; color: #fff; padding:5px 10px 5px 5px;font-size: 12px; font-family:'Arial';
                                        border-bottom: 10px solid silver;"><strong>Margen final s/conductor</strong></th>
                                        <th width="15%%" style="background-color: #a24689; color: #fff; padding:5px 10px 5px 5px;font-size: 12px; font-family:'Arial';
                                        border-bottom: 10px solid silver;"><strong>Ingreso Operacion</strong></th>
                                        <th width="15%%" style="background-color: #a24689; color: #fff; padding:5px 10px 5px 5px;font-size: 12px; font-family:'Arial';
                                        border-bottom: 10px solid silver;"><strong>Estado </strong></th>
                                    </tr>
                                    %s
                                    <br/>
                                    %s
                                    </tbody>
                                </table>
                                <br/><br/>
                                <table style="border-collapse:collapse; margin: 0 auto; width:
                                100%%; background:inherit; color:inherit">
                                    <tbody>
                                     <tr>
                                        <h2 style="font-size:18px; font-family:'Arial'; color: #a24689;">
                                            Margen Alto <b style="font-size:16px;">(mayor a 54%%)</b>
                                        </h2>
                                    </tr>
                                    <tr>
                                        <th width="15%%" style="background-color: #a24689; color: #fff; padding:5px 10px 5px 5px;font-size: 12px; font-family:'Arial';
                                        border-bottom: 10px solid silver;"><strong>Cliente</strong></th>
                                        <th width="15%%" style="background-color: #a24689; color: #fff; padding:5px 10px 5px 5px;font-size: 12px; font-family:'Arial';
                                        border-bottom: 10px solid silver;"><strong>Num de Viaje</strong></th>
                                        <th width="15%%" style="background-color: #a24689; color: #fff; padding:5px 10px 5px 5px;font-size: 12px; font-family:'Arial';
                                        border-bottom: 10px solid silver;"><strong>Unidad</strong></th>
                                        <th width="15%%" style="background-color: #a24689; color: #fff; padding:5px 10px 5px 5px;font-size: 12px; font-family:'Arial';
                                        border-bottom: 10px solid silver;"><strong>Ruta</strong></th>
                                        <th width="15%%" style="background-color: #a24689; color: #fff; padding:5px 10px 5px 5px;font-size: 12px; font-family:'Arial';
                                        border-bottom: 10px solid silver;"><strong>Fecha</strong></th>
                                        <th width="15%%" style="background-color: #a24689; color: #fff; padding:5px 10px 5px 5px;font-size: 12px; font-family:'Arial';
                                        border-bottom: 10px solid silver;"><strong>Costo total estimado s/conductor</strong></th>
                                        <th width="15%%" style="background-color: #a24689; color: #fff; padding:5px 10px 5px 5px;font-size: 12px; font-family:'Arial';
                                        border-bottom: 10px solid silver;"><strong>Margen Estimado s/conductor</strong></th>
                                        <th width="15%%" style="background-color: #a24689; color: #fff; padding:5px 10px 5px 5px;font-size: 12px; font-family:'Arial';
                                        border-bottom: 10px solid silver;"><strong>Costo al liquidar s/conductor</strong></th>
                                        <th width="15%%" style="background-color: #a24689; color: #fff; padding:5px 10px 5px 5px;font-size: 12px; font-family:'Arial';
                                        border-bottom: 10px solid silver;"><strong>Margen final s/conductor</strong></th>
                                        <th width="15%%" style="background-color: #a24689; color: #fff; padding:5px 10px 5px 5px;font-size: 12px; font-family:'Arial';
                                        border-bottom: 10px solid silver;"><strong>Ingreso Operacion</strong></th>
                                        <th width="15%%" style="background-color: #a24689; color: #fff; padding:5px 10px 5px 5px;font-size: 12px; font-family:'Arial';
                                        border-bottom: 10px solid silver;"><strong>Estado </strong></th>
                                    </tr>
                                    %s
                                    <br/>
                                    %s
                                    </tbody>
                                </table>
                            </div>
                          """ % (self.env.user.company_id.name, table1, footer1, table2, footer2, table3, footer3)
        if not email_to:
            email_to = self.env['ir.config_parameter'].sudo().get_param('send_alert_travel_mg.receivers_email', 'False')
            # email_to = 'salmon@gebesa.com,cesar.barron@gebesa.com,deysy.mascorro@gebesa.com,samuel.barron@gebesa.com,luis.cabrales@transportesgalbo.com,contabilidad@transportesgalbo.com'
        mail = mail_obj.create({
            'subject': 'Viajes liquidados Ayer',
            'email_to': email_to,
            'headers': "{'Return-Path': u'odoo@gebesa.com'}",
            'body_html': body_mail,
            'auto_delete': True,
            'message_type': 'comment',
        })
        mail.send()
