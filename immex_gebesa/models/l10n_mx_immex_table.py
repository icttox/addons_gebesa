# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class L10nMxImmexTable(models.Model):
    _name = 'l10n.mx.immex.table'
    _description = 'descripcion pendiente'

    typestr = fields.Char(
        string='Type',
    )

    type_id = fields.Many2one(
        'l10n.mx.immex.table.type',
        string='Internal type',
    )

    field_name = fields.Char(
        string='Name',
    )

    field_value = fields.Char(
        string='Value',
    )

    wizard_id = fields.Integer(
        string='Wizard',
    )

    rownum = fields.Integer(
        string='Row number',
    )
