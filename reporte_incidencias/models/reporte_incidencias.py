# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order.line'

    date = fields.Char(
        string='Date Order',
        compute="_compute_report_",
    )

    nom = fields.Char(
        string='Order',
        compute="_compute_report_",
    )

    ref = fields.Char(
        string='Order Reference',
        compute="_compute_report_",
    )

    proj = fields.Char(
        string='Project',
        compute="_compute_report_",
    )

    ship = fields.Char(
        string='Partner Shipping',
        compute="_compute_report_",
    )

    note = fields.Char(
        string='Note',
        compute="_compute_report_",
    )

    qty = fields.Char(
        string='Quantity',
        compute="_compute_report_",
    )

    amou = fields.Char(
        string='Amount',
        compute="_compute_report_",
    )

    stat = fields.Char(
        string='State',
        compute="_compute_report_",
    )

    code = fields.Char(
        string='Product',
        compute="_compute_report_",
    )

    produ = fields.Char(
        string='Product Name',
        compute="_compute_report_",
    )

    repl = fields.Char(
        string='Reason',
        compute="_compute_report_",
    )

    part = fields.Char(
        string='Partner',
        compute="_compute_report_",
    )

    team = fields.Char(
        string='Order Team',
        compute="_compute_report_",
    )

    @api.multi
    def _compute_report_(self):
        prod_obj = self.env['product.product']
        for sale in self:
            prod_var = prod_obj.search([('default_code', '=', sale.product_id.default_code),('active', '=', True)])
            if sale.order_id:
                if prod_var:
                    for order in sale.order_id:
                        if order.priority == 'replenishment':
                            if order.name:
                                sale.date = order.date_order
                                sale.nom = order.name
                                sale.stat = order.state
                                sale.part = order.partner_id.name
                                sale.ref = order.client_order_ref
                                sale.proj = order.analytic_account_id.name
                                sale.ship = order.partner_shipping_id.name
                                sale.note = order.note
                                sale.qty = sale.product_uom_qty
                                sale.amou = sale.product_uom_qty * sale.standard_cost
                                sale.code = sale.product_id.default_code
                                sale.produ = sale.product_id.name_template
                                sale.repl = order.replenishing_motif
                                sale.team = order.team_id.name
