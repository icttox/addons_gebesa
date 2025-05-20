# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    skip_supply_mo = fields.Boolean(
        string='Skip supply in MO',
    )
    skip_handover_mo = fields.Boolean(
        string='Skip handover in MO',
    )
