# -*- coding: utf-8 -*-
# © 2021 Leslie Marquez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ItSoftwareEquipmentRel(models.Model):
    _name = 'it.software.equipment.rel'
    _description = 'descripcion pendiente'

    it_software_id = fields.Many2one(
        'it.software',
        string='IT Software',
    )

    equipment_id = fields.Many2one(
        'maintenance.equipment',
        string='Maintenance Equipment',
    )

    valid = fields.Boolean(
        string='Valid',
    )
