# -*- coding: utf-8 -*-
# © <2017> <César Barrón Butista>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockMove(models.Model):
    _name = 'stock.move'
    _inherit = 'stock.move'

    def get_last_split_move(self):
        descendant = self
        qty = 0.000000
        last_desc = self
        while descendant:
            if descendant.state == 'done':
                qty += descendant.product_qty
            last_desc = descendant
            descendant = self.env['stock.move'].search(
                [('split_from', '=', descendant.id)]) or False

        return last_desc, qty
