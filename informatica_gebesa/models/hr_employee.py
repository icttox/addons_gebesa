# -*- coding: utf-8 -*-
# © <2018> <Aldo Nerio>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    equipment_ids = fields.One2many(
        'maintenance.equipment',
        'employee_id',
        string='Equipment',
    )
