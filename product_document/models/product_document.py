# -*- coding: utf-8 -*-
# Copyright YEAR(S), AUTHOR(S)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductDocument(models.Model):
    _name = 'product.document'
    _description = 'descripcion pendiente'

    link = fields.Char(
        string='Link',
        required=True,
    )

    description = fields.Text(
        string='Description',
        required=True,
    )

    product_type = fields.Selection(
        [('plano', 'Plano'),
         ('plano_laser', 'Plano y Laser'),
         ('isometrico', 'Isometrico'),
         ('render', 'Render'),
         ('manual', 'Manual'),
         ('laser', 'Laser'),
         ('3d_model', 'Modelado 3D'),
         ('etiqueta', 'Etiqueta')],
        string="Type",
        required=True,
    )

    change_log = fields.Text(
        string='Change log',
    )

    revision = fields.Char(
        string='Document revision',
        required=True,
        default='V0',
    )

    product_template_id = fields.Many2one(
        'product.template',
        string='Product',
    )

    is_line = fields.Boolean(
        string='Line Product',
        readonly=True,
        related='product_template_id.is_line',
    )
