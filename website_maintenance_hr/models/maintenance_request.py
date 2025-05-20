# Copyright 2022, Samuel Barron
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class MaintenanceRequest(models.Model):
    _inherit = 'maintenance.request'

    image = fields.Binary(string='Image')
