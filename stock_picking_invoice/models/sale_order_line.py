# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    def _action_procurement_create(self):
        procurement = super()._action_procurement_create()

        move_obj = self.env['stock.move']
        for move in move_obj.search([('procurement_id', 'in', [
                ids.id for ids in procurement])]):
            move.invoice_state = 'none'
            if move.picking_id.sale_id.invoice_status == 'to invoice':
                move.invoice_state = '2binvoiced'

        return procurement
