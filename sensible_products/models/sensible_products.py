# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class SensibleProducts(models.Model):
    _name = 'sensible.products'
    _description = 'descripcion pendiente'
    # _description = 'Description'

    # _id---> Referencia que es un campo externo(Base de datos)
    location_id = fields.Many2one(
        'stock.location',
        string='Location',
    )

    product_id = fields.Many2one(
        'product.product',
        string='Product',
    )
