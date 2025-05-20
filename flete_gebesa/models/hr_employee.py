# -*- coding: utf-8 -*-
# © <2018> <Aldo Nerio>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class hr_employee(models.Model):
    _inherit = 'hr.employee'

    employee_event_id = fields.One2many(
        'hr.employee.event',
        'employee_id',
        string='Employee'
    )
