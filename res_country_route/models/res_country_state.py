# Copyright 2024, Samuel Barron
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class ResCountryState(models.Model):
    _inherit = 'res.country.state'

    route_id = fields.Many2one(
        'res.country.route',
        string='Route',
    )
