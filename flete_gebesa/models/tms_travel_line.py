from __future__ import division

from odoo import api, fields, models
import odoo.addons.decimal_precision as dp


class TmsTravelLine(models.Model):
    _name = 'tms.travel.line'
    _description = 'Waybill Line'
    _order = 'sequence, id desc'

    travel_id = fields.Many2one(
        'tms.travel',
        string='Waybill',
        readonly=True)
    name = fields.Char('Description', required=True)
    sequence = fields.Integer(
        help="Gives the sequence order when displaying a list of "
        "sales order lines.",
        default=10)
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
        domain=[('sale_ok', '=', True)])
    unit_price = fields.Float(
        default=0.0)
    price_subtotal = fields.Float(
        compute='_compute_amount_line',
        string='Subtotal')
    tax_amount = fields.Float()
    tax_ids = fields.Many2many(
        'account.tax', string='Taxes',
        domain='[("type_tax_use", "=", "sale")]')
    product_qty = fields.Float(
        string='Quantity',
        digits=dp.get_precision('Product Unit of Measure'),
        default=1.000)
    discount = fields.Float(
        string='Discount (%)',
        help="Please use 99.99 format...")
    account_id = fields.Many2one(
        'account.account',
        string='Account')

    @api.onchange('product_id')
    def on_change_product_id(self):
        for rec in self:
            rec.name = rec.product_id.name
            fpos = rec.travel_id.partner_id.property_account_position_id
            fpos_tax_ids = fpos.map_tax(rec.product_id.taxes_id)
            rec.tax_ids = fpos_tax_ids
            rec.write({
                'account_id': rec.product_id.property_account_income_id.id
            })

    @api.multi
    @api.depends('product_qty', 'unit_price', 'discount')
    def _compute_amount_line(self):
        for rec in self:
            price_discount = (
                rec.unit_price * ((100.00 - rec.discount) / 100))
            taxes = rec.tax_ids.compute_all(
                price_discount, rec.travel_id.currency_id,
                rec.product_qty, rec.product_id,
                rec.travel_id.partner_id)
            rec.price_subtotal = taxes['total_excluded']
            rec.tax_amount = taxes['total_included'] - taxes['total_excluded']
