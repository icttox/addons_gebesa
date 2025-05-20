# Copyright 2022, Marco Esquivel
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class HrPayslipLine(models.Model):
    _inherit = 'hr.payslip.line'

    exempt = fields.Float(
        string='Exempt',
    )

    taxed = fields.Float(
        string='Taxed',
    )
