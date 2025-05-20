# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    review = fields.Selection([
        ('no_review', 'No Review'),
        ('yes_review', 'Review')],
        string='Warehouse Review',
        track_visibility='onchange',
        default='no_review')

    @api.multi
    def action_review(self):
        for order in self:
            if order.review == 'no_review':
                self.write({'review': 'yes_review'})
                for line in order.order_line:
                    reviewed = True
                    line.reviewed = reviewed
            else:
                raise UserError(_("This purchase order has already "
                                  "been reviewed by the Warehouse Manager"))
        return True

    @api.multi
    def button_confirm(self):
        for order in self:
            if order.review == 'no_review':
                raise UserError(_("Can not confirm the order until it \
                    is reviewed"))
            if not self.env.user.company_id.is_manufacturer:
                if not self.env.user.has_group('purchase_order_review_status.group_validation_the_po_lines_unit_price'):
                    for line in order.order_line:
                        if line.product_id.type == 'product':
                            sale_line = self.env['sale.order.line'].search([
                                ('id', '=', line.sale_line_id.id),
                                ('product_id.type', '=', 'product')], limit=1)
                            if sale_line:
                                margen = round(sale_line.price_unit * 0.90, 2)
                                if line.price_unit == sale_line.price_unit or line.price_unit >= margen:
                                    raise UserError("El precio unitario del producto %s debe de tener un 10%% de margen del precio unitario de la venta " % line.product_id.default_code)
        return super().button_confirm()


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    reviewed = fields.Boolean(
        string='Valid',
        track_visibility='onchange')

    origin = fields.Char(
        related='order_id.origin',
        readonly=True,
        stored=True)

    warehouse_id = fields.Many2one(
        'stock.warehouse',
        related='order_id.warehouse_id',
        string='Warehouse',
        store=True,
        readonly=True)

    @api.multi
    @api.constrains('reviewed')
    def _update_valid_po(self):
        for line in self:
            lines = len(line.order_id.order_line)
            valid_lines = len(
                self.env['purchase.order.line'].search(
                    [('order_id', '=', line.order_id.id),
                     ('reviewed', '=', True)]))
            if valid_lines == lines:
                if line.order_id.review != 'yes_review':

                    line.order_id.review = 'yes_review'
            else:
                if line.order_id.review != 'no_review':

                    line.order_id.review = 'no_review'
