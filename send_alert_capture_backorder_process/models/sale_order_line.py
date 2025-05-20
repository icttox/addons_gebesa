# Copyright 2022, Samuel Barron
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _data_alert_capture_backorder_process(self):
        self._cr.execute(
            """
            SELECT * FROM (
                SELECT
                    sw.name AS warehouse,
                    pf.name AS family,
                    ROUND(
                        SUM(
                            CASE WHEN so.state IN ('sale', 'done') AND sol.product_uom_qty != 0
                                    AND so.geb_invoice_status in ('no_invoice','partial_invoice')
                            THEN (sol.pending_qty * (sol.net_sale / sol.product_uom_qty)) * so.rate_mex
                            ELSE 0.00 END)
                        , 2) AS amount_backorder,
                    COALESCE(pf.weekly_sales_goal, 0.00) AS weekly_sales_goal,
                    ROUND(
                        CAST(SUM(
                            CASE WHEN CAST(so.date_validator AT TIME ZONE 'UTC' AT TIME ZONE 'America/Mexico_City' AS DATE) BETWEEN
                                CAST(NOW() AT TIME ZONE 'America/Mexico_City' - (INTERVAL '1 DAYS' * (date_part('dow', now()) + 6)) AS DATE) AND
                                CAST(NOW() AT TIME ZONE 'America/Mexico_City' - (INTERVAL '1 DAYS' * date_part('dow', now())) AS DATE)
                            THEN sol.net_sale_mx ELSE 0.00 END
                        ) AS NUMERIC)
                    , 2) AS amount_captura
                FROM sale_order_line AS sol
                INNER JOIN sale_order AS so ON sol.order_id = so.id
                INNER JOIN product_product AS pp ON sol.product_id = pp.id
                INNER JOIN product_template AS pt ON pp.product_tmpl_id = pt.id
                INNER JOIN product_family AS pf ON pt.family_id = pf.id
                LEFT JOIN stock_warehouse AS sw ON pf.warehouse_id = sw.id
                WHERE  so.state NOT IN ('draft', 'sent', 'cancel')
                    AND sol.closed IS NOT TRUE
                    AND so.company_id = %s
                GROUP BY sw.id,pf.id
                ORDER BY sw.id,pf.name
            ) AS T1 WHERE amount_backorder > 0 OR amount_captura > 0
            """, ([self.env.user.company_id.id]))
        if not self._cr.rowcount:
            return False
        return self._cr.fetchall()

    @api.model
    def alert_capture_backorder_process(self):

        data = self._data_alert_capture_backorder_process()
        table = """"""
        rows = """"""
        warehouse = data[0][0]
        tot_bo = 0
        tot_os = 0
        tot_cs = 0
        for line in data:
            if warehouse != line[0]:
                week = 0.00
                if tot_os > 0.00:
                    week = tot_bo / tot_os
                color = "#84ee62"
                if tot_cs < tot_os:
                    color = "#ff6d6d"
                table += """
                    <tr>
                        <td align="left" style="border-bottom: 1px solid silver; color: #000; font-size: 14px; font-family:'Arial';"><b>%s</b></td>
                        <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 14px; font-family:'Arial';"><b>%s</b></td>
                        <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 14px; font-family:'Arial';"><b>%s</b></td>
                        <td align="center" bgcolor="%s" style="border-bottom: 1px solid silver; color: #000; font-size: 14px; font-family:'Arial';"><b>%s</b></td>
                        <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 14px; font-family:'Arial';"><b>%s</b></td>
                    </tr>
                """ % (warehouse, "{:,.2f}".format(tot_bo), "{:,.2f}".format(tot_os), color, "{:,.2f}".format(tot_cs), "{:,.2f}".format(week))
                table += rows
                rows = """"""
                warehouse = line[0]
                tot_bo = 0
                tot_os = 0
                tot_cs = 0

            week = 0.00
            if line[3] > 0.00:
                week = line[2] / line[3]
            color = "#84ee62"
            if line[4] < line[3]:
                color = "#ff6d6d"
            rows += """
                <tr>
                    <td align="left" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                    <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                    <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                    <td align="center" bgcolor="%s" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                    <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 12px; font-family:'Arial';">%s</td>
                </tr>
            """ % (line[1], "{:,.2f}".format(line[2]), "{:,.2f}".format(line[3]), color, "{:,.2f}".format(line[4]), "{:,.2f}".format(week))

            tot_bo += line[2]
            tot_os += line[3]
            tot_cs += line[4]

        week = 0.00
        if tot_os > 0.00:
            week = tot_bo / tot_os
        color = "#84ee62"
        if tot_cs < tot_os:
            color = "#ff6d6d"
        table += """
            <tr>
                <td align="left" style="border-bottom: 1px solid silver; color: #000; font-size: 14px; font-family:'Arial';"><b>%s</b></td>
                <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 14px; font-family:'Arial';"><b>%s</b></td>
                <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 14px; font-family:'Arial';"><b>%s</b></td>
                <td align="center" bgcolor="%s" style="border-bottom: 1px solid silver; color: #000; font-size: 14px; font-family:'Arial';"><b>%s</b></td>
                <td align="center" style="border-bottom: 1px solid silver; color: #000; font-size: 14px; font-family:'Arial';"><b>%s</b></td>
            </tr>
        """ % (warehouse, "{:,.2f}".format(tot_bo), "{:,.2f}".format(tot_os), color, "{:,.2f}".format(tot_cs), "{:,.2f}".format(week))
        table += rows

        body_mail = u"""
            <div summary="o_mail_notification" style="padding:0px; width:90%%;
             margin:0 auto; background: #FFFFFF repeat top /100%%; color:#777777">
                <table cellspacing="0" cellpadding="0" style="width:100%%;
                border-collapse:collapse;">
                    <tbody><tr>
                        <td valign="center" width="270" style="padding:5px 10px
                         5px 5px;font-size: 17px; font-family:'Arial';">
                            <b>Captura y BO por Proceso</b>
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
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Planta/Proceso</strong></th>
                        <th width="10%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Backorder</strong></th>
                        <th width="10%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Objetivo Semanal</strong></th>
                        <th width="6%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Captura Semana</strong></th>
                        <th width="7%%" style="padding:5px 10px 5px 5px; font-size: 15px; font-family:'Arial';
                        border-bottom: 10px solid silver; background-color: #a24689;"><strong>Semanas de Trabajo</strong></th>
                    </tr>
                    %s
                    </tbody>
                </table>
            </div>
          """ % (self.env.user.company_id.name, table)

        destinatarios = self.env['ir.config_parameter'].sudo().get_param('send_alert.capture_backorder_process', 'False')
        mail = self.env['mail.mail'].create({
            'subject': 'Captura y BO por Proceso',
            'email_to': destinatarios,
            'headers': "{'Return-Path': u'odoo@gebesa.com'}",
            'body_html': body_mail,
            'auto_delete': True,
            'message_type': 'comment',
        })
        mail.send()
