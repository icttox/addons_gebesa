# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api
from odoo.exceptions import ValidationError
from odoo.addons import decimal_precision as dp


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    margin_justification = fields.Char(
        string='P. M. Justification',
        size=100,
        help='Low-margin justification for the invoice',
    )

    net_sale = fields.Float(
        string='Net Sales',
        digits=dp.get_precision('Account'),
    )

    freight_amount = fields.Float(
        string='Freight Amount',
        digits=dp.get_precision('Account'),
    )

    installation_amount = fields.Float(
        string='Installation Amount',
        digits=dp.get_precision('Account'),
    )

    standard_cost = fields.Float(
        string='Standard Cost',
        digits=dp.get_precision('Account'),
    )

    total_cost = fields.Float(
        string='Total Cost',
        digits=dp.get_precision('Account'),
    )

    profit_margin = fields.Float(
        string='Profit Margin',
        digits=dp.get_precision('Account'),
    )

    @api.model
    def create(self, vals):
        if self.env.user.has_group('account_invoice_sale_data.invoice_lines_from_orders'):
            return super().create(vals)
        invoice_id = vals.get('invoice_id')
        if invoice_id:
            invoice = self.env['account.invoice'].browse(invoice_id)
            if invoice.type == 'out_invoice' and invoice.sale_id:
                product_id = vals.get('product_id')
                product = self.env['product.product'].browse(product_id)
                product_ids = invoice.sale_id.order_line.mapped('product_id.id')
                if product_id not in product_ids and product.type == 'product':
                    raise ValidationError('The product %s is not on the sales order lines for billing.' % product.default_code)
        return super().create(vals)

    @api.multi
    def write(self, vals):
        if self.env.user.has_group('account_invoice_sale_data.invoice_lines_from_orders'):
            return super().write(vals)
        product_id = vals.get('product_id', self.product_id.id)
        if self.invoice_id.type == 'out_invoice' and self.invoice_id.sale_id:
            product = self.env['product.product'].browse(product_id)
            product_ids = self.invoice_id.sale_id.order_line.mapped('product_id.id')
            if product_id not in product_ids and product.type == 'product':
                raise ValidationError('The product %s is not on the sales order lines for billing.' % product.default_code)
        return super().write(vals)
