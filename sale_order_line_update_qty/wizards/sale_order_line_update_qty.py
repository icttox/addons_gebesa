# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleOrderLineUpdateQty(models.TransientModel):
    _name = 'sale.order.line.update.qty'
    _description = 'descripcion pendiente'

    qty_delivered = fields.Float(
        string='Delivered',
    )
    qty_invoiced = fields.Float(
        string='Invoiced',
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
    )
    product_uom_qty = fields.Float(
        string='Quantity',
    )

    @api.multi
    def update_qty(self):
        active_ids = self.env['sale.order.line'].browse(
            self._context.get('active_ids', []))
        # import ipdb; ipdb.set_trace()
        if 0 > self.qty_delivered or 0 > self.qty_invoiced:
            raise ValidationError(_('The quantities to be updated must be \
                greater than or equal to zero.'))
        if self.qty_delivered > self.product_uom_qty:
            raise ValidationError(_('The quantity sent must be less than the \
                quantity ordered.'))
        if self.qty_invoiced > self.product_uom_qty:
            raise ValidationError(_('The quantity invoiced must be less than \
                the amount ordered.'))
        for line in active_ids:
            line.qty_delivered = self.qty_delivered
            line.qty_invoiced = self.qty_invoiced
