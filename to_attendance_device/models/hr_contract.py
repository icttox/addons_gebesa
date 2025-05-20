# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class HrContract(models.Model):
    _inherit = 'hr.contract'

    def get_default_overtime(self):
        if self.env.user.company_id.is_manufacturer:
            return 50
        return 0

    max_overtime = fields.Integer(
        string='Horas extra maximas',
        default=get_default_overtime
    )
