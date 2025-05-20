# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api
from odoo.addons import decimal_precision as dp


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    margin_justification = fields.Char(
        string='P. M. justification',
        size=100,
        help='low-margin justification for the sales order',
    )

    net_sale = fields.Float(
        string='Net sales',
        digits=dp.get_precision('Account'),
        compute='_compute_profit_margin',
        store=True
    )

    freight_amount = fields.Float(
        string='Freight amount',
        digits=dp.get_precision('Account'),
        compute='_compute_profit_margin',
        store=True
    )

    installation_amount = fields.Float(
        string='installation amount',
        digits=dp.get_precision('Account'),
        compute='_compute_profit_margin',
        store=True
    )

    standard_cost = fields.Float(
        string='Standard cost',
        digits=dp.get_precision('Account'),
        compute='_compute_profit_margin',
        store=True
    )

    purchase_price_geb = fields.Float(
        string='Cost',
        digits=dp.get_precision('Account'),
        compute='_compute_purchase_price_geb',
        store=True
    )

    profit_margin = fields.Float(
        string='Profit margin',
        digits=dp.get_precision('Account'),
        compute='_compute_profit_margin',
        store=True
    )

    low_mu = fields.Boolean(
        string='Bajo M.U.',
        compute='_compute_low_mu',
        default=False
    )

    volume = fields.Float(
        string='Volume',
        related='product_id.volume'
    )
    #  @api.multi
    # def _check_mu(self):
    #    for record in self:
    #       record.product_id.product_templ_id.group_id.mu.min
    #      if mugroup > 0:
    #         if mugroup > record.profit_margin
    #            record.low_mu = True
    #   else:
    #      muline = record.product_id.product_templ_id.line_id.mu.min
    #      if muline > 0:

    @api.depends('product_id', 'price_unit', 'product_uom_qty')
    def _compute_purchase_price_geb(self):
        for record in self:
            record.purchase_price_geb = record.product_id.standard_price or 0.0

    @api.depends('profit_margin', 'price_unit', 'order_id.perc_freight',
                 'order_id.perc_installation')
    def _compute_low_mu(self):
        for record in self:
            mugroup = record.product_id.product_tmpl_id.group_id.mu_min
            muline = record.product_id.product_tmpl_id.line_id.mu_min
            if mugroup > 0:
                if mugroup > record.profit_margin:
                    record.low_mu = True
            elif muline > 0:
                if muline > record.profit_margin:
                    record.low_mu = True

    @api.depends('price_unit', 'product_uom_qty', 'order_id.perc_freight',
                 'order_id.perc_installation', 'discount')
    def _compute_profit_margin(self):
        for record in self:
            currency = record.order_id.company_id.currency_id
            product = record.product_id
            standard_cost = product.standard_price or 0.0
            total_cost = standard_cost * record.product_uom_qty
            perc_freight = record.order_id.perc_freight or False
            freight = 0.0
            profit_margin = 0.0
            perc_installation = record.order_id.perc_installation or False
            installation = 0.0
            net_sale = (1 - (record.discount / 100)) * (
                record.price_unit * record.product_uom_qty)
            if perc_freight:
                freight = net_sale * (perc_freight / 100)
            net_sale = net_sale - freight
            if perc_installation:
                installation = net_sale * (perc_installation / 100)
            net_sale = net_sale - installation

            if net_sale > 0.000000:
                # total_pm = currency.compute(
                #     total_cost, record.order_id.pricelist_id.currency_id)
                total_pm = currency._convert(
                    total_cost, record.order_id.pricelist_id.currency_id, record.order_id.company_id, fields.Date.today())
                profit_margin = (1 - (total_pm) / net_sale)
                profit_margin = profit_margin * 100

            record.freight_amount = freight
            record.installation_amount = installation
            record.net_sale = net_sale
            record.profit_margin = profit_margin
            # record.purchase_price_geb = standard_cost
            record.standard_cost = total_cost

    @api.multi
    def write(self, vals):
        if 'product_id' in vals:
            product = self.env['product.product'].browse([vals['product_id']])
            if product:
                vals['purchase_price_geb'] = product.standard_price or 0.0

        return super().write(vals)
