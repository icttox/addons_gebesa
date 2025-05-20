# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    show_web_portal = fields.Boolean(
        string='Show in Portal',
        default=False,
        store=True,
    )

    hubspot_user = fields.Boolean(
        string='Hubspot',
        default=False,
    )
