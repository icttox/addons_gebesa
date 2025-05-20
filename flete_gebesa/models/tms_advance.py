# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models


class TmsAdvance(models.Model):
    _inherit = 'tms.advance'

    @api.multi
    def action_confirm(self):
        super().action_confirm()
        for rec in self:
            vehicle = rec.unit_id
            for line in rec.move_id.line_ids:
                line.analytic_account_id = vehicle.account_analytic_id.id
                line.product_id = rec.product_id.id
