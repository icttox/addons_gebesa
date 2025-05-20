# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockLocationRoute(models.Model):
    _inherit = 'stock.location.route'

    family_ids = fields.Many2many(
        'product.family',
        string="Preferred for family",
    )

    is_manufacture = fields.Boolean(
        string='It is to manufacture',
    )

    tsca = fields.Boolean(
        string='TSCA',
    )

    route_default = fields.Boolean(
        string='Add default in products',
    )
