# -*- coding: utf-8 -*-
# Copyright 2024, Samuel Barron
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import time
from odoo import api, models
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def action_procurement_processes(self):
        for production in self:
            pickings_raw = production.picking_raw_material_ids.filtered(
                lambda pick: pick.state not in ('draft', 'cancel', 'done'))
            for picking in pickings_raw:
                move_to_done = self.env['stock.move']
                moves = picking.move_ids_without_package.filtered(
                    lambda x: x.state in ('draft', 'waiting', 'confirmed',
                                          'assigned', 'partially_available'))
                for move in moves:
                    move_raw_material = move.move_dest_ids.filtered(
                        lambda x: x.raw_material_production_id.id == production.id)

                    if not move_raw_material:
                        continue

                    quantity_done = sum(
                        move_raw_material.mapped('product_uom_qty'))

                    quantity_done -= sum(move_raw_material.mapped('move_orig_ids').filtered(
                        lambda x: x.state in ('done', 'cancel')).mapped('product_uom_qty'))

                    move.quantity_done = quantity_done
                    move.write({'state': 'assigned'})
                    if not move.price_unit:
                        move.write({
                            'price_unit': move.product_id.standard_price})
                    move_to_done += move

                move_to_done._action_done()

                if not picking.date_done:
                    picking.write({'date_done': time.strftime(
                        DEFAULT_SERVER_DATETIME_FORMAT)})

    def action_transfer_processes(self):
        for production in self:
            qty_create = sum(production.move_finished_ids.filtered(
                lambda x: x.state == 'done').mapped('product_uom_qty'))

            qty_transfer = sum(production.move_dest_ids.filtered(
                lambda x: x.state == 'done').mapped('product_uom_qty'))

            qty = qty_create - qty_transfer
            for move in production.move_dest_ids.filtered(
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

    @api.multi
    def action_all_processes(self):
        productions = self.filtered(
            lambda prod: prod.state not in ('draft', 'cancel'))
        for production in productions:
            if production.state == 'progress':
                raise UserError(
                    "La MO %s ya esta en proceso, no puede usar esta opcion" % production.name)

            # PROCUREMENT
            production.action_procurement_processes()

            # PRODUCE
            ctx = self.env.context.copy()
            ctx.update({'active_id': production.id})
            vals = self.env['mrp.product.produce'].with_context(ctx).default_get(
                ['serial', 'production_id', 'product_id', 'product_qty',
                 'product_uom_id', 'product_tracking', 'lot_id',
                 'produce_line_ids'])
            produce = self.env['mrp.product.produce'].create(vals)
            produce._onchange_product_qty()
            produce.do_produce()

            # TRANSFER
            production.action_transfer_processes()

            if production.state not in ('cancel', 'transfer'):
                if production.state != 'done':
                    production.button_mark_done()
                production._compute_transfer_status()
            self.env.cr.commit()
