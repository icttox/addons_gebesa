# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import models, api


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    @api.model
    def match_cost_sentinel(self):
        query = """
            SELECT
                pp.id as pp_id,
                pp.default_code as clave,
                pp.name_template,
                pp.individual_name,
                ip.value_float as valuee,
                bom.id AS bom_id,
                br.name AS route,
                sum(ip2.value_float * mbl.product_qty) as sumatoria,
                ip.value_float - sum(ip2.value_float * mbl.product_qty) AS diferencia
            FROM product_product as pp
            LEFT JOIN ir_property AS ip ON CONCAT('product.product,',pp.id)=ip.res_id
                AND ip.name='standard_price' AND ip.fields_id=2804
                AND ip.company_id = 1
            JOIN mrp_bom as bom on bom.product_id = pp.id
            LEFT JOIN mrp_routing AS br ON bom.routing_id = br.id
            LEFT JOIN mrp_bom_line as mbl ON mbl.bom_id = bom.id
            join ir_property ip2 on ip2.fields_id = 2804 and ip2.res_id = concat('product.product,',mbl.product_id)
                AND ip2.company_id = 1
            WHERE pp.default_code is not null
                AND pp.active
                AND bom.active
                AND ip.value_float is not null
                AND ip.value_float != 0
                AND bom.company_id = 1
            GROUP BY pp.id,ip.id,bom.id,br.id
            HAVING ABS(ROUND(CAST(ip.value_float AS numeric),2) - ROUND(CAST(sum(ip2.value_float * mbl.product_qty) AS numeric),2)) >= 0.05
            ORDER BY pp.default_code, pp.name_template limit 500;
        """
        # self.env.cr.execute(query, tuple(params))
        self.env.cr.execute(query)
        desfasados = self.env.cr.dictfetchall()
        table = ''
        for desfase in desfasados:
            clave = desfase['clave']

            products = self.env[
                'product.product'].search(
                    [('default_code', '=', clave)], limit=1)

            if not products:
                continue

            prod = products[0]

            boms = self.env[
                'mrp.bom'].search(
                    [('product_id', '=', prod.id),
                     ('active', '=', True)])

            numboms = self.env[
                'mrp.bom'].search_count(
                    [('product_id', '=', prod.id),
                     ('active', '=', True)])

            if not boms:
                continue

            if numboms == 1:
                detalle = boms[0]
                detalle.action_reval()
                self.env.cr.commit()

                table += """
                    <tr><td align="center" style="border-bottom: 1px solid silver;">%s</td>
                        <td align="center" style="border-bottom: 1px solid silver;">%s</td>
                        <td align="center" style="border-bottom: 1px solid silver;">%s</td>
                        <td align="center" style="border-bottom: 1px solid silver;">%s</td>
                        <td align="center" style="border-bottom: 1px solid silver;">%s</td>
                    </tr>
                """ % (clave, desfase['valuee'], desfase['sumatoria'], desfase['diferencia'],str(datetime.now()))

        mail_obj = self.env['mail.mail']
        body_mail = u"""
            <div summary="o_mail_notification" style="padding:0px; width:700px;
            margin:0 auto; background: #FFFFFF repeat top /100%%; color:#777777">
                <table cellspacing="0" cellpadding="0" style="width:100%%;
                border-collapse:collapse; background:inherit; color:inherit">
                    <tbody><tr>
                        <td align="center" width="270" style="padding:5px 10px
                        5px 5px;font-size: 18px">
                            <p>
                            <strong>Sent by</strong>
                            <a href="http://erp.portalgebesa.com" style="text-
                            decoration:none; color: #a24689;">
                            <strong>%s</strong>
                            </a>
                            <strong>using</strong>
                            <a href="https://www.odoo.com" style="text-
                            decoration:none; color: #a24689;"><strong>Odoo
                        </strong></a>
                        </p>
                        </td>
                </tr>
                </tbody><table>
            </div>
            <div style="padding:0px; width:700px; margin:0 auto; background:
            #FFFFFF repeat top /100%%; color:#777777">
                <table cellspacing="0" cellpadding="0" style="vertical-align:
                top; padding:0px; border-collapse:collapse; background:inherit;
                color:inherit">
                    <tbody><tr>
                        <td valign="top" style="width:700px; padding:5px 10px
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
                1100px; background:inherit; color:inherit">
                    <tbody><tr>
                        <th width="15%%" style="padding:5px 10px 5px 5px;font-
                        size: 14px; border-bottom: 2px solid silver;"><strong>
                        Clave</strong></th>
                        <th width="15%%" style="padding:5px 10px 5px 5px;font-
                        size: 14px; border-bottom: 2px solid silver;"><strong>
                        Costo</strong></th>
                        <th width="15%%" style="padding:5px 10px 5px 5px;font-
                        size: 14px; border-bottom: 2px solid silver;"><strong>
                        Detalle</strong></th>
                        <th width="15%%" style="padding:5px 10px 5px 5px;font-
                        size: 14px; border-bottom: 2px solid silver;"><strong>
                        Diferencia</strong></th>
                        <th width="15%%" style="padding:5px 10px 5px 5px;font-
                        size: 14px; border-bottom: 2px solid silver;"><strong>
                        Timestamp</strong></th>
                    </tr>
                    %s
                    </tbody>
                </table>
            </div>
          """ % (self.env.user.company_id.name, table)
        if table != '':
            mail = mail_obj.create({
                'subject': 'Productos con costo desfasado corregidos',
                'email_to': 'cesar.barron@gebesa.com,deysy.mascorro@gebesa.com,samuel.barron@gebesa.com',
                'headers': "{'Return-Path': u'odoo@gebesa.com'}",
                'body_html': body_mail,
                'auto_delete': True,
                'message_type': 'comment',
            })
            mail.send()
