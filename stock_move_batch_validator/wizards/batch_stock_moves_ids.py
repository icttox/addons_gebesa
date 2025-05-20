# -*- coding: utf-8 -*-
# © 2016 Cesar Barron
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class BatchStockMovesIds(models.TransientModel):
    _name = 'batch.stock.moves.ids'
    _description = 'group of stock moves ids for validate'

    sm_ids = fields.Text(
        string='Ids for validate',
        required=True,)

    @api.multi
    def action_validate_all(self):

        # import ipdb
        # ipdb.set_trace()
        errors = ""
        for rec in self:
            split_ids = rec.sm_ids.split(',')
            for idr in split_ids:
                smove = self.env['stock.move'].browse(int(idr))

                try:
                    smove._force_assign()
                    smove._action_assign()
                    smove._action_done()
                except ValueError as exc:
                    errors += "Error({0}): {1}".format(exc.errno, exc.strerror)

        return True
