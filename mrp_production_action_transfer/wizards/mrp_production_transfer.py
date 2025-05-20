# -*- coding: utf-8 -*-
# © 2017 Cesar Barron
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import time
from odoo import api, models
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class MrpProductionTransfer(models.TransientModel):
    _name = 'mrp.production.transfer'
    _description = 'descripcion pendiente'

    @api.multi
    def mrp_production_transfer(self):
        production_obj = self.env['mrp.production']

        active_ids = self._context.get('active_ids', []) or []
        production = production_obj.browse(active_ids)

        for prod in production:
            if prod.state not in ['done', 'progress']:
                continue

            qty_create = sum(prod.move_finished_ids.filtered(
                lambda x: x.state == 'done').mapped('product_uom_qty'))

            qty_transfer = sum(prod.move_dest_ids.filtered(
                lambda x: x.state == 'done').mapped('product_uom_qty'))

            qty = qty_create - qty_transfer
            for move in prod.move_dest_ids.filtered(
                    lambda x: x.state not in ('done', 'cancel')):
                if qty > 0:
                    if move.product_uom_qty >= qty:
                        move.write({
                            'quantity_done': qty,
                            'state': 'assigned'})
                        qty -= qty
                    else:
                        move.write({
                            'quantity_done': move.product_uom_qty,
                            'state': 'assigned'})
                        qty -= move.product_uom_qty
                    move._action_done()

                if not move.picking_id.date_done:
                    move.picking_id.write({'date_done': time.strftime(
                        DEFAULT_SERVER_DATETIME_FORMAT)})
            self.env.cr.commit()
