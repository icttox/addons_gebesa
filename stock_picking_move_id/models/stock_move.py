# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class StockMove(models.Model):
    _inherit = 'stock.move'

    acc_move_id = fields.Many2one(
        'account.move',
        string='Account Move',
        copy=False
    )

    def _action_done(self):
        res = super()._action_done()
        # account_move_ids
        for picking in self.mapped('picking_id'):
            acc_move_ids = []
            for s_move in self.filtered(
                    lambda move: move.picking_id.id == picking.id):
                acc_move_ids.extend(
                    [(4, a_move.id) for a_move in s_move.account_move_ids])
            picking.write({'am_ids': acc_move_ids})

        for raw_prod in self.mapped('raw_material_production_id'):
            acc_move_ids = []
            for s_move in self.filtered(
                    lambda move: move.raw_material_production_id.id == raw_prod.id):
                acc_move_ids.extend(
                    [(4, a_move.id) for a_move in s_move.account_move_ids])
            raw_prod.write({'am_ids': acc_move_ids})

        for prod in self.mapped('production_id'):
            acc_move_ids = []
            for s_move in self.filtered(
                    lambda move: move.production_id.id == prod.id):
                acc_move_ids.extend(
                    [(4, a_move.id) for a_move in s_move.account_move_ids])
            prod.write({'am_ids': acc_move_ids})

        return res
