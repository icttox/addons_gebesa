# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError


class SaleOrderLineUpdatePriceWizard(models.TransientModel):
    _name = 'sale.order.line.update.price.wizard'
    _description = 'descripcion pendiente'

    price_unit = fields.Float(
        'Unit Price',
        required=True,
        digits=dp.get_precision('Product Price'),
        default=0.0
    )

    @api.multi
    def update_price(self):
        order_line_ids = self.env['sale.order.line'].browse(
            self._context.get('active_ids', []))
        for line in order_line_ids:
            if line.qty_invoiced > 0:
                raise UserError(
                    "La linea del producto %s ya esta facturada, no puede cambiar el precio" % line.product_id.default_code)
            line.order_id.state = 'sale'
            line.price_unit = self.price_unit
            line.order_id.state = 'done'
