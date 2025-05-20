# -*- coding: utf-8 -*-
# © 2018 Aldo Nerio
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class LogisticUnitType(models.Model):
    _name = 'logistic.unit.type'
    _rec_name = 'name'
    _description = 'descripcion pendiente'

    name = fields.Char(
        string='Name',
    )
    description = fields.Text(
        string='Description',
    )
    width = fields.Float(
        string='Width',
    )
    empty_weight = fields.Float(
        string='Empty Weight',
    )
    height = fields.Float(
        string='Height',
    )
    lenght = fields.Float(
        string='Lenght',
    )

    _sql_constraints = [
        ('name_uniq', 'unique (name)',
         'The name must be unique! ')
    ]
