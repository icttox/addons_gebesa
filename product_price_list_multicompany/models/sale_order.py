# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    is_manufacturer = fields.Boolean(
        related='company_id.is_manufacturer',
        string='Is manufacturer',
        readonly=True
    )

    partner_sellers_ids = fields.Many2many(
        'res.users',
        string='Sellers',
        related='partner_id.sellers_ids',
    )
    partner_salesrep_ids = fields.Many2many(
        'res.users',
        string='Salesrep',
        compute="_compute_partner_salesrep_ids"
    )

    @api.multi
    @api.onchange('salesrep_id')
    def _compute_partner_salesrep_ids(self):
        for sale in self:
            sale.partner_salesrep_ids = sale.salesrep_id.salesrep_ids

    @api.multi
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        super().onchange_partner_id()
        if self.env.user.company_id.country_id.code != 'MX':
            if not self.partner_id:
                self.user_id = False
                self.salesrep_id = False
                self.sales_person_id = False
            else:
                self.user_id = False
                self.sales_person_id = False
                self.salesrep_id = self.partner_id.salesrep_ids[0].id if len(self.partner_id.salesrep_ids) == 1 else False

    @api.multi
    def create_product_supplierinfo(self):
        buy_id = self.env.ref('purchase_stock.route_warehouse0_buy').id
        make_to_order_id = self.env['stock.location.route'].search([
            ('name', 'like', 'Bajo Pedido%')], limit=1).id
        partner_id = self.env['res.company'].sudo().search([(
            'is_manufacturer', '=', True
        )], limit=1).partner_id
        if not partner_id:
            raise UserError("No supplier found")
        for sale in self:
            for line in sale.order_line:
                supplierinfo = line.product_id.variant_seller_ids.filtered(
                    lambda s: s.product_id.id == line.product_id.id)
                if not supplierinfo:
                    self.env['product.supplierinfo'].create({
                        'name': partner_id.id,
                        'product_id': line.product_id.id,
                        'min_qty': 0,
                        'currency_id': sale.company_id.currency_id.id,
                        'product_tmpl_id': line.product_id.product_tmpl_id.id,
                        'price': 0,
                        'delay': 1
                    })
                # if not line.product_id.purchase_ok:
                #     line.product_id.purchase_ok = True
                line.product_id.sudo().write({
                    'purchase_ok': True,
                    'route_ids': [(4, buy_id), (4, make_to_order_id)]
                })
