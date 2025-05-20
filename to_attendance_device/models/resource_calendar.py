# Copyright 2022, Samuel Barron
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class ResourceCalendar(models.Model):
    _inherit = 'resource.calendar'

    tolerance_time = fields.Float(
        string='Tolerance',
    )
