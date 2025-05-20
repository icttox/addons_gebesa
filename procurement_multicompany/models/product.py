# -*- coding: utf-8 -*-
# © 2017 Cesar Barron
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def _compute_quantities_dict(self, lot_id, owner_id, package_id, from_date=False, to_date=False):
        res = super(ProductProduct, self)._compute_quantities_dict(
            lot_id=lot_id, owner_id=owner_id, package_id=package_id,
            from_date=from_date, to_date=to_date)
        order_id = self._context.get('force_sale_order', False)
        if order_id:
            for product in self:
                if product.id in res.keys():
                    qty_out = sum(order_id.order_line.filtered(
                        lambda line: line.product_id.id == product.id).mapped('product_uom_qty'))
                    res[product.id]['outgoing_qty'] += qty_out
                    res[product.id]['virtual_available'] -= qty_out
        return res
