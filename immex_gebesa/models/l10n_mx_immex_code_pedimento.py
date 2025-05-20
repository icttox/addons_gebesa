# -*- coding: utf-8 -*-
# © 2021, Leslie Marquez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class L10nMxImmexCodePedimento(models.Model):
    _name = 'l10n.mx.immex.code.pedimento'
    _description = 'descripcion pendiente'

    code = fields.Char(
        string='Code',
    )
    name = fields.Char(
        string='Name',
    )
    description = fields.Char(
        string='Description',
    )
