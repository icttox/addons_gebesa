# -*- coding: utf-8 -*-
# © 2021, Leslie Marquez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductPricelistCategory(models.Model):
    _name = "product.pricelist.category"
    _description = "Product Pricelist Category"

    name = fields.Char(
        string='Name',
    )

    isometric = fields.Binary(
        string="Isometric image",
        attachment=True,
        store= True,
    )
