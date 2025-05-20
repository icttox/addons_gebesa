# Copyright 2024, Marco Esquivel
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    partner_hubspot = fields.Char(
        string='Partner HubSpot',
    )
