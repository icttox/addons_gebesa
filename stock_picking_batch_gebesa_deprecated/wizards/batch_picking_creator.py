# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models
from odoo.exceptions import UserError


class StockBatchPickingCreator(models.TransientModel):
    _inherit = 'stock.batch.picking.creator'

    @api.multi
    def action_create_batch(self):
        pickings = self.env['stock.picking'].search([
            ('id', 'in', self.env.context['active_ids']),
            ('batch_picking_id', '=', False),
            ('state', 'not in', ('cancel', 'done'))
        ])
        if not pickings:
            raise UserError(_(
                "There's no one picking to be grouped"
            ))

        location = pickings[0].location_id
        for pick in pickings:
            if pick.location_id != location:
                raise UserError(_(
                    "Only picking from the same source store can be chosen"
                ))
        return super().action_create_batch()
