# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class MrpProductionDailyLoad(models.Model):
    _inherit = 'mrp.production.daily.load'

    employee_id = fields.Many2one(
        'hr.employee',
        string='Empleado',
    )
