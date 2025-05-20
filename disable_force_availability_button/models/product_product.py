# Copyright 2020, Cesar Barron
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.multi
    def action_view_stock_moves(self):
        stock_moves = self.env['stock.move'].search(
            [('product_id', '=', self.id)])
        action = self.env.ref('stock.stock_move_action').read()[0]
        if stock_moves:
            action['domain'] = [('id', 'in', stock_moves.ids)]
            action['context'] = {'search_default_done': 0, 'search_default_groupby_location_id': 1}
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
