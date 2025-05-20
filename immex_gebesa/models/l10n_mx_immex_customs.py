# -*- coding: utf-8 -*-
# © 2021, Leslie Marquez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class L10nMxImmexCustoms(models.Model):
    _name = 'l10n.mx.immex.customs'
    _description = 'descripcion pendiente'

    code = fields.Char(
        string='Code',
    )
    section = fields.Char(
        string='Section',
    )
    name = fields.Char(
        string='Name',
    )
