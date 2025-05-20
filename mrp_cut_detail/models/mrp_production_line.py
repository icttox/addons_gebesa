# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class MrpProductionLine(models.Model):
    _name = 'mrp.production.line'
    _rec_name = "description"
    _description = 'descripcion pendiente'

    code = fields.Char(
        string='Code',
    )
    description = fields.Char(
        string='Description',
    )
