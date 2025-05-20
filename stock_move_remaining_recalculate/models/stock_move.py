# -*- coding: utf-8 -*-
# © 2021, Samuel Barron, Gebesa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from odoo import api, models, tools
# from odoo.tools.float_utils import float_compare

_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.model
    def move_remaining_recalculated_auto(self):
        company_ids = self.env['res.company'].sudo().search([
            ('is_manufacturer', '=', False)])
        for company in company_ids:
            locations = self.env['stock.location'].search([
                ('usage', '=', 'internal'),
                ('active', '=', True),
                ('company_id', '=', company.id)])

            for loc in locations:
                self._cr.execute("""
                    SELECT
                        *
                    FROM (
                        SELECT
                            pp.id AS product_id,
                            pp.default_code AS codigo,
                            pp.name_template AS producto,
                            ROUND(SUM(CASE WHEN sm.location_id = sm.location_dest_id THEN 0
                                WHEN sm.location_dest_id = %s THEN sm.product_qty ELSE sm.product_qty * -1 END), 6) AS existencia,
                            ROUND(CAST(sm_rem.remaining_qty AS NUMERIC), 6) AS remaining_qty
                        FROM product_product pp
                        JOIN stock_move sm on pp.id = sm.product_id
                        JOIN (
                            SELECT
                                product_id,
                                SUM(remaining_qty) AS remaining_qty
                            FROM stock_move
                            WHERE location_dest_id = %s
                                AND state = 'done'
                            GROUP BY product_id)  AS sm_rem ON pp.id = sm_rem.product_id
                        WHERE (sm.location_dest_id = %s OR sm.location_id = %s)
                            AND sm.state = 'done'
                            AND sm.company_id = %s
                        GROUP BY pp.id,sm_rem.remaining_qty) AS datas
                    WHERE existencia != remaining_qty
                    """, (
                    loc.id, loc.id, loc.id, loc.id, loc.company_id.id))
                for prod in self._cr.fetchall():

                    move_neg_ids = self.env['stock.move'].search([
                        ('location_id', '=', loc.id),
                        ('product_id', '=', prod[0]),
                        ('remaining_qty', '<', 0)])

                    for move_neg in move_neg_ids:
                        qty_to_remaining = tools.float_round(
                            abs(move_neg.remaining_qty),
                            precision_rounding=move_neg.product_id.uom_id.rounding,
                            rounding_method='UP')
                        move_ids = self.env['stock.move'].search([
                            ('location_dest_id', '=', loc.id),
                            ('product_id', '=', prod[0]),
                            ('remaining_qty', '>', 0)])
                        for move in move_ids:
                            cost_unit = move.remaining_value / move.remaining_qty
                            remaining_qty = tools.float_round(
                                abs(move.remaining_qty),
                                precision_rounding=move.product_id.uom_id.rounding,
                                rounding_method='UP')

                            if remaining_qty >= qty_to_remaining:
                                new_qty = remaining_qty - qty_to_remaining
                                qty_to_remaining -= qty_to_remaining
                            else:
                                qty_to_remaining -= remaining_qty
                                new_qty = remaining_qty - remaining_qty

                            new_cost = cost_unit * new_qty

                            move.write({
                                'remaining_qty': new_qty,
                                'remaining_value': new_cost
                            })

                            if qty_to_remaining == 0:
                                break

                        cost_unit_neg = move_neg.remaining_qty / abs(move_neg.remaining_qty)
                        new_cost_neg = cost_unit_neg * qty_to_remaining
                        move_neg.write({
                            'remaining_qty': qty_to_remaining,
                            'remaining_value': new_cost_neg
                        })
