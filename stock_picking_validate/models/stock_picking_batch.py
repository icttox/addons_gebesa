# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockPicking(models.Model):
    _inherit = 'stock.picking.batch'

    def validate_batch_done(self):
        batch_ids = self.search([('state', '=', 'in_progress')])

        for batch in batch_ids:
            if batch.picking_ids and all(
                    [picking.state in ('done', 'cancel') for picking in batch.picking_ids]):
                batch.done()
