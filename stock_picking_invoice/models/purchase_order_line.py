# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.multi
    def _create_stock_moves(self, picking):
        moves = super()._create_stock_moves(picking)

        for move in moves:
            move.invoice_state = 'none'
            if move.picking_id.purchase_id.invoice_status == 'to invoice':
                move.invoice_state = '2binvoiced'
        return moves
