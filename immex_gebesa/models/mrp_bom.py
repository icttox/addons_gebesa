# -*- coding: utf-8 -*-
from odoo import models, fields


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    salida_a24 = fields.Boolean(
        related='product_id.salida_a24',
        string='Salida A24'
    )
