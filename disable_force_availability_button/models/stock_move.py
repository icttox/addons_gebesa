# -*- coding: utf-8 -*-
# © <2018> <Aldo Nerio>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _force_assign(self):
        """ Allow to work on stock move lines even if the reservationis not
        possible. We just mark the move as assigned, so the view does not block
        the user.
        """
        for move in self.filtered(lambda m: m.state in [
                'confirmed', 'waiting', 'partially_available', 'assigned']):
            if move.quantity_done < move.product_uom_qty:
                move.write({'quantity_done': move.product_uom_qty})
            move.write({'state': 'assigned'})
