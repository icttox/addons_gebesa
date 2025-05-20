# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ProductAttributeValueEquivalent(models.Model):
    _name = 'product.attribute.value.equivalent'
    _description = 'descripcion pendiente'

    attribute_origin_id = fields.Many2one(
        'product.attribute',
        string='Attribute Origin',
        required=True
    )
    value_origin_id = fields.Many2one(
        'product.attribute.value',
        string='Value Origin',
        required=True
    )
    attribute_id = fields.Many2one(
        'product.attribute',
        string='Attribute',
        required=True
    )
    value_id = fields.Many2one(
        'product.attribute.value',
        string='Value',
        required=True
    )
    name = fields.Char(
        string='Name',
    )

    @api.onchange('value_origin_id', 'value_id')
    def _onchange_name(self):
        name = ""
        name += self.attribute_origin_id.name or ""
        name += ":"
        name += self.value_origin_id.name or ""
        name += " - "
        name += self.attribute_id.name or ""
        name += ":"
        name += self.value_id.name or ""
        self.name = name

    _sql_constraints = [
        ('values_unique',
         'UNIQUE(value_origin_id,value_id)',
         "The combination of values is already defined"),
    ]
