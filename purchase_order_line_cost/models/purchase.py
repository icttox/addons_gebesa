# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    # @api.onchange('order_line')
    # def _onchange_order_line(self):
    #     for purchase in self:
    #         domain = []
    #         for line in purchase.order_line:
    #             partner = []
    #             seller_ids = line.product_id.seller_ids
    #             if not seller_ids:
    #                 return {'domain': {'partner_id': [('id', 'in', '[]')]}}
    #             if not domain:
    #                 for seller in seller_ids:
    #                     domain.append(seller.name.id)
    #             else:
    #                 for seller in seller_ids:
    #                     if seller.name.id in domain:
    #                         partner.append(seller.name.id)
    #                 domain = partner
    #         if purchase.partner_id.id not in domain:
    #             purchase.partner_id = None
    #     return {'domain': {'partner_id': [('id', 'in', domain)]}}


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    standard_price = fields.Float(
        string='Standard price',
        # related='product_id.standard_price',
        compute='_compute_standard_price',
        store=True,
    )

    @api.depends('product_id')
    def _compute_standard_price(self):
        for line in self:
            line.standard_price = line.product_id.standard_price


class StockMove(models.Model):
    _inherit = 'stock.move'

    standard_price = fields.Float(
        string='Standard price',
        compute='_compute_standard_price',
        store=True,
    )

    @api.depends('product_id')
    def _compute_standard_price(self):
        for move in self:
            move.standard_price = move.product_id.standard_price
