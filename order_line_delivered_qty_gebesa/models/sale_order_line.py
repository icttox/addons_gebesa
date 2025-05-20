# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import math
from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    def _compute_qty_delivered(self):
        super(SaleOrderLine, self)._compute_qty_delivered()

        for line in self:
            if line.qty_delivered_method == 'stock_move':
                bom = self.env['mrp.bom']._bom_find(product=line.product_id, company_id=line.company_id.id)
                if bom and bom.type == 'phantom':
                    moves = line.move_ids.filtered(
                        lambda m: m.location_dest_id.usage == 'customer')

                    products = {}
                    delivered = {}
                    for move in moves:
                        if move.product_id.id not in products.keys():
                            products[move.product_id.id] = 0
                        products[move.product_id.id] += move.product_uom_qty
                        if move.state == 'done':
                            if move.product_id.id not in delivered.keys():
                                delivered[move.product_id.id] = 0
                            delivered[move.product_id.id] += move.product_uom_qty

                    percent = 100
                    for prod in products:
                        if prod in delivered:
                            percent_new = (100 * delivered[prod]) / products[prod]
                        else:
                            percent_new = 0

                        if percent_new < percent:
                            percent = percent_new

                    parte_decimal, delivered_qty = math.modf(
                        line.product_uom_qty * (percent / 100))
                    line.qty_delivered = delivered_qty
