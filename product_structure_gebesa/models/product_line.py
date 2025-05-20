# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductLine(models.Model):
    _name = 'product.line'
    _description = 'product.line'
    _order = "name asc"

    code = fields.Char(
        string='Code',
        size=5,
        required=True,
        help='Line code product',
    )

    name = fields.Char(
        string='Name',
        size=120,
        required=True,
        help='Line name product',
    )

    product_family_id = fields.Many2one(
        'product.family',
        string='Product Family',
    )

    active = fields.Boolean(
        string='Active',
        default=True
    )

    report_type = fields.Selection(
        [('normal', 'NORMAL'),
         ('modulares', 'MODULARES')],
        string="Type Report",
    )

    mu_min = fields.Float(
        string='M.U. Minimum'
    )
