# -*- coding: utf-8 -*-
# © 2018 Aldo Nerio
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models, fields


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    approved = fields.Boolean(
        string='Approve',
        default=False,
        copy=False,
    )

    @api.multi
    def approved_check(self):
        self.approved = True
