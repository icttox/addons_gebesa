

from odoo import models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def cancel_moves_so_cancel(self):
        self._cr.execute("""
            UPDATE stock_move AS sm
            SET state = 'cancel'
            FROM procurement_group AS pg
            INNER JOIN sale_order AS so ON pg.name = so.name
            WHERE (so.state = 'cancel' OR (so.state = 'closed' AND so.cancel_mo))
            AND NOT sm.state IN ('assigned', 'done')
            AND sm.group_id = pg.id""")

        # Cancel movelines y desreservar, para stock_moves_cancelados:
        # Asi es, no filtra solo los movimientos de este pedido, es a proposito
        # No deberian ser muchos
        self._cr.execute("""
            UPDATE stock_move_line
                SET state = 'cancel',
                product_qty = 0.00000
            FROM stock_move sm
            WHERE sm.id = stock_move_line.move_id
            AND sm.state = 'cancel' AND stock_move_line.state != 'cancel'
        """)

        # Cancela los pickings que tienen todos sus moves cancelados
        self._cr.execute("""
            UPDATE stock_picking sp SET state = 'cancel'
            WHERE sp.id IN (
                SELECT
                    sp.id AS picking_id
                FROM stock_picking AS sp
                JOIN stock_move AS sm ON sp.id = sm.picking_id
                WHERE sp.state NOT IN ('done', 'cancel')
                GROUP BY sp.id
                HAVING COUNT(sm.id) = SUM(CASE WHEN sm.state = 'cancel' THEN 1 ELSE 0 END)
            )
        """)

        # Cancela las ordenes de fabricacion
        self._cr.execute("""
            UPDATE mrp_production AS mp SET state = 'cancel'
            WHERE mp.id IN (
                SELECT
                    mp.id
                FROM mrp_production AS mp
                INNER JOIN sale_order AS so ON mp.sale_id = so.id
                WHERE (so.state = 'cancel' OR (so.state = 'closed' AND so.cancel_mo))
                    AND mp.state IN ('draft', 'confirmed')
            )
        """)
