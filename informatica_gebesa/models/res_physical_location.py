# -*- coding: utf-8 -*-
# © <2018> <Daniel Gurrola>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResPhysicalLocation(models.Model):
    _name = 'res.physical.location'
    _description = 'descripcion pendiente'

    code = fields.Char(
        string='Codigo',
    )

    name = fields.Char(
        string='Nombre',
    )
    parent_id = fields.Many2one(
        'res.physical.location',
        string='Parent',
    )
