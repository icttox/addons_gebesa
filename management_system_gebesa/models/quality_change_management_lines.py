# Copyright 2022, Marco Esquivel
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields


class QualityChangeManagementLines(models.Model):
    _name = 'quality.change.management.lines'
    _description = 'descripcion pendiente'

    activities = fields.Text(
        string='Activities',
        required=True,
    )

    responsible_id = fields.Many2one(
        'hr.employee',
        string='Responsible',
    )

    date_execution = fields.Date(
        string='Date execution',
        default=fields.Date.context_today,
    )

    change_lines_id = fields.Many2one(
        'quality.change.management',
    )
