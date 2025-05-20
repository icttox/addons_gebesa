# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    int_buyer = fields.Integer(
        string='ID Buyer',
    )


class ProductProduct(models.Model):
    _inherit = 'product.product'

    preferred_supplier_id = fields.Many2one(
        'res.partner',
        string='Preferred Supplier',
    )

    product_origin = fields.Selection([
        ('national', 'National'),
        ('import', 'import'),
        ('internal_process', 'Internal process'),
        ('external_machine', 'External machine')],
        string='Origin',
        copy=False,)

    rawmat_rotation = fields.Selection([
        ('recurrent', 'Habitual'),
        ('special', 'Especial')],
        string='Tipo de rotación',
        copy=False,)

    import_preference = fields.Boolean(
        string='Preferentemente importacion',
    )
