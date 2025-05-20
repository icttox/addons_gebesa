# -*- coding: utf-8 -*-
# © <2017> Aldo Nerio
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductAttributeLine(models.Model):
    _inherit = 'product.template.attribute.line'

    name_web = fields.Char(
        string='Web Name'
    )
