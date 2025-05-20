# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class L10nMxImmexTableType(models.Model):
    _name = 'l10n.mx.immex.table.type'
    _description = 'descripcion pendiente'

    code = fields.Char(
        string='Code',
    )

    name = fields.Char(
        string='Name',
    )

    level = fields.Selection(
        [('pedimento', 'Pedimento'),
         ('partida', 'Partida')],
        string="Level",
    )

    active = fields.Boolean(
        string='Active',
        default=True,
    )
