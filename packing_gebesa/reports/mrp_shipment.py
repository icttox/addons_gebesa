# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import math
from odoo import api, models


class ParticularReport(models.AbstractModel):
    _inherit = 'report.mrp_shipment.report_shipment'

    @api.multi
    def search_range_packing(self, line, num_packing):
        bom_obj = self.env['mrp.bom']
        packing_obj = self.env['product.packing.list']
        product_obj = self.env['product.product']
        total_page = 0
        page_product_kit = {}
        if line.packing_id:
            if line.packing_id.qty > 0:
                total_qty = line.quantity_shipped
                tagged_qty = line.packing_id.qty
                total_page = math.ceil(total_qty / tagged_qty)
            elif line.packing_id.packing_line_ids:
                total_page = 0
                for packig_line in line.packing_id.packing_line_ids:
                    total_qty = line.quantity_shipped
                    tagged_qty = packig_line.quantity
                    total_page += math.ceil(total_qty / tagged_qty)
        else:
            bom = bom_obj.search([
                ('product_id', '=', line.product_id.id),
                ('active', '=', True)])
            if bom.type == 'phantom':
                self._cr.execute(
                    """
                    WITH RECURSIVE componentes(
                        product_id, code, qty, not_kit, r) AS (
                        SELECT
                            pp.id,
                            pp.default_code,
                            ROUND((
                                mbl.product_qty / mb.product_qty) * 1,6
                                ) AS product_qty,
                            CASE WHEN mb2.type = 'phantom'
                                THEN FALSE ELSE TRUE END AS not_kit,
                            CAST(ROW_NUMBER () OVER () AS TEXT)
                        FROM mrp_bom AS mb
                        JOIN mrp_bom_line AS mbl ON mb.id = mbl.bom_id
                        JOIN product_product AS pp
                            ON mbl.product_id = pp.id
                        LEFT JOIN mrp_bom AS mb2
                            ON pp.id = mb2.product_id
                        WHERE mb.product_id = %s
                            AND mb.type = 'phantom'
                        UNION SELECT
                            pp.id,
                            pp.default_code,
                            ROUND(c.qty * ((
                                mbl.product_qty / mb.product_qty) * 1),
                                 6) AS product_qty,
                            CASE WHEN mb2.type = 'phantom'
                                THEN FALSE ELSE TRUE END AS not_kit,
                            CONCAT(c.r, '-', CAST(
                                ROW_NUMBER () OVER () AS TEXT))
                        FROM componentes AS c
                        LEFT JOIN mrp_bom AS mb
                            ON c.product_id = mb.product_id
                        JOIN mrp_bom_line AS mbl ON mb.id = mbl.bom_id
                        JOIN product_product AS pp
                            ON mbl.product_id = pp.id
                        JOIN mrp_bom AS mb2 ON pp.id = mb2.product_id
                        WHERE c.not_kit IS false
                    )
                    SELECT product_id, code, SUM(qty) FROM componentes
                    WHERE not_kit GROUP BY product_id, code
                    ORDER BY code, product_id""",
                    ([line.product_id.id]))
                if self._cr.rowcount:
                    tot_pag = 0
                    num_pack = num_packing
                    for row in self._cr.fetchall():
                        product_det = product_obj.browse([row[0]])
                        packing = packing_obj.search([
                            ('product_tmpl_id', '=',
                             product_det.product_tmpl_id.id),
                            ('active', '=', True),
                            ('type', '=', 'standard')
                        ])
                        if not packing:
                            page_product_kit[product_det.id] = {
                                'total_page': 0,
                                'min_page': num_packing,
                                'max_page': num_packing,
                            }
                            tot_pag += 0
                        else:
                            if packing.qty > 0:
                                total_qty = line.quantity_shipped * row[2]
                                tagged_qty = packing.qty
                                pag = math.ceil(total_qty / tagged_qty)
                                page_product_kit[product_det.id] = {
                                    'total_page': pag,
                                    'min_page': num_pack + 1,
                                    'max_page': num_pack + pag,
                                }
                                tot_pag += pag
                                num_pack += pag
                            elif packing.packing_line_ids:
                                pag = 0
                                for packig_line in packing.packing_line_ids:
                                    total_qty = line.quantity_shipped
                                    tagged_qty = packig_line.quantity
                                    pag += math.ceil(total_qty / tagged_qty)
                                page_product_kit[product_det.id] = {
                                    'total_page': pag,
                                    'min_page': num_pack + 1,
                                    'max_page': num_pack + pag,
                                }
                                tot_pag += pag
                                num_pack += pag
                    total_page = tot_pag
        if total_page > 0:
            min_page = num_packing + 1
            max_page = num_packing + total_page
        else:
            min_page = num_packing
            max_page = num_packing

        data = {
            'total_page': total_page,
            'min_page': min_page,
            'max_page': max_page,
            'page_product_kit': page_product_kit
        }
        return data
