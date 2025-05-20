# -*- coding: utf-8 -*-

from odoo import api, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.one
    def inter_company_create_sale_order(self, company):
        purchase = super().inter_company_create_sale_order(company)
        for po in self:
            so = po.order_line.mapped('sale_line_id').mapped('order_id')
            so.write({'supplier_ref': po.partner_ref})
        return purchase
