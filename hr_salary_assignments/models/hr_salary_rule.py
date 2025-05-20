from odoo import fields, models

class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    show_in_payslip = fields.Boolean(
        string='Show in payslip lines',
        help="Show rule in payslip lines",
        default=True
    )
    novelty = fields.Boolean()
