# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def _default_warehouse_id(self):
        company = self.env.user.company_id
        warehouse_id = company.sale_warehouse_id
        return warehouse_id.id

    @api.model
    def _default_analytic_account_id(self):
        company = self.env.user.company_id
        analytic_account = company.sale_project_id
        return analytic_account.id

    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        'Analytic Account',
        readonly=True,
        states={'draft': [('readonly', False)],
                'sent': [('readonly', False)]},
        help="The analytic account related to a sales order.",
        copy=False,
        default=_default_analytic_account_id,
        oldname='project_id',
        domain=[('account_type', '=', 'normal')])

    warehouse_id = fields.Many2one(
        'stock.warehouse', string='Warehouse',
        required=True, readonly=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        default=_default_warehouse_id)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.model
    def _default_route_id(self):
        route_id = False
        if self.product_id:
            route_id = self.env['stock.location.route'].search(
                [('family_ids', '=', self.product_id.family_id.id)])
            if route_id:
                route_id = route_id[0].id
        return route_id

    route_id = fields.Many2one(
        'stock.location.route',
        string='Route',
        default=_default_route_id,
        domain=[('sale_selectable', '=', True)])
