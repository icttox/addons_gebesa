# -*- coding: utf-8 -*-

from odoo import models, fields


class ProductProduct(models.Model):
    _inherit = 'product.product'

    product_uom = fields.Many2one(
        'uom.uom',
        string='Unidad Tigie',
    )
    salida_a24 = fields.Boolean(
        string='Salida A24',
    )


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    immex_type_id = fields.Many2one(
        'l10n.mx.immex.partida.type',
        string='Immex Clasificación'
    )
    apply_download_immex = fields.Boolean(
        string='Apply download immex',
    )
