# Copyright 2022, Marco Esquivel
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields


class HrDepartment(models.Model):
    _name = 'hr.department'
    _inherit = 'hr.department'

    show_incidents = fields.Boolean(
        string='Show incidents',
    )
