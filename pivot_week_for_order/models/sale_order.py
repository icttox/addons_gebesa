# -*- coding: utf-8 -*-
# © <2017> <Aldo Nerio>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # amount_pending_total = fields.Monetary(
    #     store=True,
    #     string='Total Amount Mex',
    #     compute='_amount_all',
    #     track_visibility='always',
    # )

    # @api.depends('amount_pending_mex')
    # def _amount_all(self):
    #     for order in self:
    #         suma = 0
    #         suma += order.amount_pending_mex
    #         order.update({
    #             'amount_pending_total': suma,
    #         })


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    date_validator = fields.Datetime(
        string='Date Validator',
        related='order_id.date_validator',
        readonly=True,
        store=True,
    )
    family_id = fields.Many2one(
        'product.family',
        string='Family',
        related='product_id.family_id',
        readonly=True,
        store=True,
    )
    warehouse_id = fields.Many2one(
        'stock.warehouse',
        string='Warehouse',
        related='product_id.family_id.warehouse_id',
        readonly=True,
        store=True,
    )
    net_sale_mx = fields.Float(
        string='Vta Neta MXN',
        compute="compute_net_sale_mex",
        readonly=True,
        store=True,
    )

    @api.depends('net_sale', 'order_id.rate_mex')
    def compute_net_sale_mex(self):
        for line in self:
            net_sale = line.net_sale
            if not line.order_id.rate_mex:
                line.net_sale_mx = net_sale
            else:
                line.net_sale_mx = net_sale * line.order_id.rate_mex
