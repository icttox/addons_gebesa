# -*- coding: utf-8 -*-
# Copyright YEAR(S), AUTHOR(S)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def action_view_fifo_distribution(self):
        action = self.env.ref(
            'stock_picking_account_location.view_stock_move_fifo_dist_action').read()[0]
        action['domain'] = [('picking_id', '=', self.ids)]
        return action

    @api.multi
    def picking_prepare_account_move(self):
        for picking in self:
            for move in picking.move_ids_without_package.filtered(lambda m: m.product_id.valuation == 'real_time' and (m._is_in() or m._is_out() or m._is_dropshipped() or m._is_dropshipped_returned())):
                move._account_entry_move()
                if move.picking_id:
                    for a_move in move.account_move_ids:
                        move.picking_id.write({'am_ids': [(4, a_move.id)]})
                if move.production_id:
                    for a_move in move.account_move_ids:
                        move.production_id.write({'am_ids': [(4, a_move.id)]})
                if move.raw_material_production_id:
                    for a_move in move.account_move_ids:
                        move.raw_material_production_id.write({
                            'am_ids': [(4, a_move.id)]})
