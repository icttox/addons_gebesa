# -*- coding: utf-8 -*-
from odoo import fields, models


class ProductTemplate(models.Model):
    # nombre de clase
    _inherit = 'product.template'
    # nombre de modelo

    category_geb_id = fields.Many2one('product.category.company.geb',
                                      company_dependent=True,
                                      string="Categoria")
