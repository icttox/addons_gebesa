# Copyright 2022, Marco Esquivel
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class HrSalaryRuleCategory(models.Model):
    _inherit = 'hr.salary.rule.category'

    type_salary = fields.Selection(
        [('perception', 'Perception'),
         ('deduction', 'Deduction')],
        string='Type salary',
    )
