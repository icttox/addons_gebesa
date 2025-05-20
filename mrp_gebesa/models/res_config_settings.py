# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    skip_supply_mo = fields.Boolean(
        related='company_id.skip_supply_mo',
        string="Skip supply in MO",
        readonly=False
    )
    skip_handover_mo = fields.Boolean(
        related='company_id.skip_handover_mo',
        string="Skip handover in MO",
        readonly=False
    )
