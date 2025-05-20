# -*- coding: utf-8 -*-
# © 2017 Cesar Barron
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class BatchPickingAccount(models.TransientModel):
    _name = 'batch.picking.account'
    _description = u'group of picking for create account entry'

    sp_names = fields.Text(
        string='Pickings',
        required=True,
    )

    @api.multi
    def action_create_entry(self):
        pick_obj = self.env['stock.picking']

        for rec in self:
            split_names = rec.sp_names.split(',')

            for sp in split_names:
                picking = pick_obj.search(
                    [('name', '=', sp)], limit=1)

                if not picking:
                    continue

                pick = picking[0]

                if pick.state not in ('done'):
                    continue

                pick.picking_prepare_account_move()
