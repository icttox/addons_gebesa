# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    type_tms_expense = fields.Selection(
        [('maniobras', 'Maneuvers'),
         ('federales', 'Federal'),
         ('permisos', 'Work Permit'),
         ('fitosanitaria', 'Phytosanitary'),
         ('pensiones', 'Pensions'),
         ('guias', 'Guides'),
         ('cocas', 'Cocas'),
         ('taxis', 'Taxis'),
         ('comidas', 'Foods'),
         ('otros', 'Otros')],
        string='Type Expenses',
        default='otros'
    )

    estimated_amount = fields.Float(
        related="product_tmpl_id.estimated_amount")

    require_travel = fields.Boolean(
        related="product_tmpl_id.require_travel")
