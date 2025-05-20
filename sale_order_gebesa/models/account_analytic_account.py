# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    use_salesorder = fields.Boolean(
        string='Analytic available for sales order',
        default=False,
    )

    warehouse_id = fields.Many2one(
        'stock.warehouse',
        string='Default warehouse',
        help='Warehouse for the sales order',
    )
