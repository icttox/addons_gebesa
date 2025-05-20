# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class L10nMxImmexPartidaType(models.Model):
    _name = 'l10n.mx.immex.partida.type'
    _description = 'descripcion pendiente'

    clave = fields.Char(
        string='Clave',
        required=True,
    )

    name = fields.Char(
        string='Name',
        required=True,
    )

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env['res.company']._company_default_get(
            'l10n.mx.immex.partida.type')
    )

    product_ids = fields.One2many(
        'product.product',
        'immex_type_id',
        string="Productos"
    )

    partida_ids = fields.One2many(
        'l10n.mx.immex.partida',
        'immex_type_id',
        string="Partidas"
    )
    download_exceptions_apply = fields.Boolean(
        string='Download exceptions apply',
    )
