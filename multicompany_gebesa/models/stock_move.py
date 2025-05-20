# -*- coding: utf-8 -*-
# Copyright YEAR(S), AUTHOR(S)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.model
    def _action_explode(self, move):
        if move.company_id.is_manufacturer:
            return super(StockMove, self)._action_explode(move)

        return [move.id]
