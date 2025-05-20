# -*- coding: utf-8 -*-
# © 2017 Aldo Nerio
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class MrpBomProductReplacement(models.Model):
    _name = 'mrp.bom.product.replacement'
    _description = 'descripcion pendiente'

    bom_line_value_id = fields.Many2one(
        'mrp.bom.line',
        string='Parent BoM Line',
        ondelete='cascade',
        index=True,
    )

    bom_product_id = fields.Many2one(
        'product.product',
        string='In product',
    )

    product_id = fields.Many2one(
        'product.product',
        string='Replace with',
    )
