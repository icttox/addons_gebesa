# Copyright 2022, Samuel Barron
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    holidays = fields.Integer(
        string='Holidays',
    )
    days_disability = fields.Integer(
        string='Days of disability',
    )
    unjustified_absences = fields.Integer(
        string='Unjustified absences',
    )
    excused_absences = fields.Integer(
        string='Excused absences',
    )
