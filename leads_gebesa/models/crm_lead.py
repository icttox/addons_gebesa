# -*- coding: utf-8 -*-
# © 2017 Aldo Nerio
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    partners_id = fields.Many2one(
        'res.partner',
        string='Channel To:',
    )

    state_free_text = fields.Char(
        string='State Name',
    )
