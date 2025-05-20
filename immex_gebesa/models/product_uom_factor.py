# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, api, models
from odoo.addons import decimal_precision as dp


class ProductUomFactor(models.Model):
    _name = 'product.uom.factor'
    _description = 'descripcion pendiente'

    unmed_origin_id = fields.Many2one(
        'uom.uom',
        string='UM Producto',
    )

    unmed_dest_id = fields.Many2one(
        'uom.uom',
        string='UMT Comercial del Pedimento',
    )

    details_ids = fields.One2many(
        'product.uom.details', 'uom_factor_id', string="Product UOM Factor")

    name = fields.Text(
        compute='_compute_name',
    )

    @api.depends('unmed_origin_id', 'unmed_dest_id')
    def _compute_name(self):
        for uom in self:
            uom.name = uom.unmed_origin_id.name + ' - ' + uom.unmed_dest_id.name


class ProductUomDetails(models.Model):
    _name = 'product.uom.details'
    _description = 'descripcion pendiente'

    product_id = fields.Many2one(
        'product.product',
        string='Product',
    )

    factor = fields.Float(
        string='Factor',
        digits=dp.get_precision('Product Unit of Measure'),
    )

    uom_factor_id = fields.Many2one(
        'product.uom.factor',
        string="Details",
    )

    partida_type_id = fields.Many2one(
        'l10n.mx.immex.partida.type',
        string='Partida Type Product',
        compute='_compute_immex_type',
    )

    @api.multi
    @api.depends('product_id')
    def _compute_immex_type(self):
        for uom in self:
            uom.partida_type_id = uom.product_id.product_tmpl_id.immex_type_id
