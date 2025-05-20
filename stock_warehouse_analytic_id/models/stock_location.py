# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockLocation(models.Model):
    _inherit = 'stock.location'

    stock_warehouse_id = fields.Many2one(
        'stock.warehouse',
        string='Stock Warehouse',
    )

    account_analytic_id = fields.Many2one(
        'account.analytic.account',
        'Analytic Account',
        related='stock_warehouse_id.account_analytic_id',
        readonly=True)

    type_stock_loc = fields.Selection(
        [('rm', 'Raw Materials'),
         ('wip', 'Work in progress'),
         ('fp', 'Finished products'),
         ('none', 'None')],
        string='Stock Type',
        default="none",)
