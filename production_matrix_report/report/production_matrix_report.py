# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, tools


class ProductionMatrixReport(models.Model):
    _name = "production.matrix.report"
    _auto = False
    _order = 'product_id'
    _rec_name = 'product_id'

    product_id = fields.Many2one(
        'product.product',
        string='Product',
    )
    pending_qty = fields.Float(
        string='Pending',
    )
    existence_qty = fields.Float(
        string='Existence',
    )
    different_qty = fields.Float(
        string='Different',
    )

    @api.model_cr
    def init(self):
        cr = self._cr
        tools.drop_view_if_exists(cr, 'production_matrix_report')
        cr.execute("""
            create or replace view production_matrix_report as (
                SELECT
                    pp.id,
                    date(NOW()) as create_date,
                    pp.id AS product_id,
                    SUM(sol.pending_qty) AS pending_qty,
                    COALESCE(SUM(ex.existencia),0.000000) AS existence_qty,
                    SUM(sol.pending_qty) - COALESCE(SUM(ex.existencia),0.000000) AS different_qty
                FROM sale_order AS so
                JOIN sale_order_line AS sol ON so.id = sol.order_id
                JOIN product_product AS pp ON sol.product_id = pp.id
                LEFT JOIN (SELECT
                        product_id,
                        SUM(CASE WHEN location_dest_id IN (SELECT id FROM stock_location WHERE type_stock_loc = 'fp')
                            THEN product_uom_qty ELSE 0 END -
                            CASE WHEN location_id IN (SELECT id FROM stock_location WHERE type_stock_loc = 'fp')
                            THEN product_uom_qty ELSE 0 END) AS existencia
                    FROM stock_move WHERE (location_id IN (SELECT id FROM stock_location WHERE type_stock_loc = 'fp')
                        OR location_dest_id IN (SELECT id FROM stock_location WHERE type_stock_loc = 'fp'))
                        AND state = 'done'
                    GROUP BY product_id) AS ex ON pp.id = ex.product_id
                WHERE so.geb_invoice_status != 'total_invoice' AND so.state != 'cancel'
                GROUP BY pp.id
                )
            """)
