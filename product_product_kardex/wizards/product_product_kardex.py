# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, _


class ProductProductKardex(models.TransientModel):
    _name = 'product.product.kardex.wizard'
    _description = 'descripcion pendiente'

    name = fields.Char(
        string='Name',
        default='KARDEX'
    )
    product_id = fields.Many2one(
        'product.product',
        string=_('Product'),
    )
    location_id = fields.Many2one(
        'stock.location',
        string=_('Location'),
    )
    fecha_inicial = fields.Date(
        string=_('Date Init'),
    )
    fecha_final = fields.Date(
        string=_('Date End'),
    )
