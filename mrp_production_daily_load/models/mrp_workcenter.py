# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class MrpWorkcenter(models.Model):
    _inherit = 'mrp.workcenter'

    daily_load_available = fields.Boolean(
        string="Daily Load Available")

    hr_department_ids = fields.Many2many(
        'hr.department',
        string='Departments',
    )
