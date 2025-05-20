# Copyright 2022, Marco Esquivel
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class HrLeaveType(models.Model):
    _inherit = 'hr.leave.type'

    time_type = fields.Selection(
        selection_add=[('vacation', 'Vacaciones'),
                       ('inhability', 'Incapacidad')]
    )
    code = fields.Char(
        string='Code',
    )
    working_days = fields.Boolean(
        string='Dias habiles',
        default=True
    )


class ResourceCalendarLeaves(models.Model):
    _inherit = "resource.calendar.leaves"

    time_type = fields.Selection(
        selection_add=[('vacation', 'Vacaciones'),
                       ('inhability', 'Incapacidad')]
    )
