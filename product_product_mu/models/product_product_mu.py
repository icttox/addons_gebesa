# -*- coding: utf-8 -*-
# © 2017 Aldo Nerio
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductProductMu(models.Model):
    _name = 'product.product.mu'
    _description = 'Type move of product'
    _order = 'code asc'
    _rec_name = 'code'

    code = fields.Char(
        string='Code', size=4,
        help='Code',
    )
    mu_dist = fields.Float(
        string='M.U.Dist',
        help='Process Dist'
    )
    mu_may = fields.Float(
        string='M.U.May',
        help='Process may'
    )
    limit_mu = fields.Float(
        string='limit.Mu',
        help='Limit'
    )
    company_id = fields.Many2one(
        'res.company', string='Company',
        help='Company'
    )
