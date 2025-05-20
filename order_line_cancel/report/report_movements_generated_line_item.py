# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ParticularReport(models.AbstractModel):
    _name = 'report.order_line_cancel.report_movements_generated_line_item'
    _description = 'descripcion pendiente'

    @api.multi
    def _get_report_values(self, docids, data=None):
        self.model = 'sale.order.line'
        docs = self.env[self.model].browse(docids)
        move_generated = {}
        for line in docs:
            self.env.cr.execute("""
                WITH RECURSIVE trazado_linea(order_array, id, picking_id, created_production_id, production_id, raw_material_production_id) AS(
                    SELECT
                        ARRAY[sm.id],
                        sm.id,
                        sm.picking_id,
                        sm.created_production_id,
                        sm.production_id,
                        sm.raw_material_production_id
                    FROM stock_move AS sm
                    JOIN stock_location AS sl ON sm.location_dest_id = sl.id
                    WHERE sm.sale_line_id = %s AND sl.usage = 'customer'
                    UNION
                        SELECT
                            tl.order_array || sm.id,
                            sm.id,
                            sm.picking_id,
                            sm.created_production_id,
                            sm.production_id,
                            sm.raw_material_production_id
                        FROM trazado_linea AS tl
                        LEFT JOIN stock_move_move_rel AS smmr ON tl.id = smmr.move_dest_id
                        JOIN stock_move AS sm ON smmr.move_orig_id = sm.id OR tl.production_id = sm.raw_material_production_id
                )
                SELECT
                    RPAD('', array_length(tl.order_array,1) - 1, '-') AS tab,
                    sm.id AS sm_id,
                    sm.state AS sm_state,
                    sl.name AS origin,
                    sl2.name AS dest,
                    pp.default_code,
                    sp.name AS picking,
                    sp.state AS pick_state,
                    mp.name AS production,
                    mp.state AS prod_state
                FROM trazado_linea AS tl
                JOIN stock_move AS sm ON tl.id = sm.id
                JOIN product_product AS pp ON sm.product_id = pp.id
                JOIN product_template AS pt ON pp.product_tmpl_id = pt.id
                JOIN stock_location AS sl ON sm.location_id = sl.id
                JOIN stock_location AS sl2 ON sm.location_dest_id = sl2.id
                LEFT JOIN stock_picking AS sp ON sm.picking_id = sp.id
                LEFT JOIN mrp_production AS mp ON COALESCE(sm.created_production_id, sm.production_id, sm.raw_material_production_id) = mp.id
                ORDER BY tl.order_array
            """ % line.id)
            move_generated[line.id] = self.env.cr.fetchall()

        docargs = {
            'doc_ids': docids,
            'doc_model': self.model,
            'docs': docs,
            'move_generated': move_generated
        }
        return docargs
