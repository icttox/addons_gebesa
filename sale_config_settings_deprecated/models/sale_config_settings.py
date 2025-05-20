# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    has_default_company = fields.Boolean(
        readonly=True,
        compute='_compute_has_default_company',
    )

    @api.depends('company_id')
    def _compute_has_default_company(self):
        count = self.env['res.company'].search_count([])
        return bool(count == 1)
