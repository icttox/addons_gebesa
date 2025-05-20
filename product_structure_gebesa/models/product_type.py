# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductType(models.Model):
    _name = 'product.type'
    _description = 'product.type'
    _order = "name asc"

    name = fields.Char(
        string='Name',
        size=120,
        required=True,
        help='Type name product',
    )

    active = fields.Boolean(
        string='Active',
        default=True
    )
