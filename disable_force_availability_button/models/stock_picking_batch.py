# -*- coding: utf-8 -*-
# © 2021 Samuel Barron, GEBESA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class StockPickingBatch(models.Model):
    _inherit = 'stock.picking.batch'

    @api.multi
    def force_assign(self):
        for batch in self:
            pickings = batch.mapped('picking_ids').filtered(
                lambda picking: picking.state not in (
                    'cancel', 'assigned', 'done'))
            for picking in pickings:
                picking.force_assign()
