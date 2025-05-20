# Copyright 2023, Cesar Barron
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, models

class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.multi
    def action_view_fifo_balance(self):

        move_ids = self.env['stock.move'].search([
            ('product_id', '=', self.id),
            ('state', '=', 'done'),
            ('remaining_qty', '>', 0.00)
        ]).ids

        tree_view = [(self.env.ref('stock_picking_account_location.stock_move_fifo_balance_tree').id, 'tree')]

        action = self.env.ref(
            'stock_picking_account_location.view_stock_move_fifo_balance_action').read()[0]
        action['domain'] = [('id', 'in', move_ids)]
        action['views'] = tree_view

        return action
