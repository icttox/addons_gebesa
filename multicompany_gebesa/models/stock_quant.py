# -*- coding: utf-8 -*-
# Copyright YEAR(S), AUTHOR(S)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models, _
from odoo.tools import float_compare
from odoo.exceptions import UserError


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.multi
    @api.constrains('product_id', 'quantity')
    def check_negative_qty(self):
        precision = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure')

        for quant in self:
            if quant.location_id.usage == 'internal':
                if (float_compare(quant.quantity, 0, precision_digits=precision) == -1 and
                        quant.product_id.type == 'product' and
                        not quant.company_id.negative_existence):
                    raise UserError(_(
                        "You cannot validate this stock operation because the "
                        "stock level of the product '%s' would become negative "
                        "on the stock location '%s' and negative stock is not "
                        "allowed for this product.") % (
                            quant.product_id.name,
                            quant.location_id.complete_name))
