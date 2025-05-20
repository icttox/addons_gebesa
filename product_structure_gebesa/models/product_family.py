# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductFamily(models.Model):
    _name = 'product.family'
    _description = 'product.family'
    _order = "name asc"

    name = fields.Char(
        string='Name',
        size=120,
        required=True,
        help='Family name product',
    )

    active = fields.Boolean(
        string='Active',
        default=True
    )

    warehouse_id = fields.Many2one(
        'stock.warehouse',
        string='Warehouse',
    )

    parent_id = fields.Many2one(
        'product.family',
        string='Padre',
    )

    analytic_id = fields.Many2one(
        'account.analytic.account',
        string='Analítica',
        company_dependent=True,
    )

    weekly_sales_goal = fields.Float(
        string='Objetivo de captura semanal',
    )
