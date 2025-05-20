# -*- coding: utf-8 -*-
# © 2017 Cesar Barron
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import time
from odoo import api, fields, models
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class MrpProductionProcure(models.TransientModel):
    _name = 'mrp.production.procure'
    _description = 'descripcion pendiente'

    include_rm = fields.Boolean(
        string="Include Raw Materials",
        help="Bring to production place the Raw matereials too.")

    include_wip = fields.Boolean(
        string="Include Work In Progress",
        help="Bring to production place the Work in progress components.")

    @api.multi
    def mrp_production_procure(self):
        production_obj = self.env['mrp.production']
        move_obj = self.env['stock.move']

        active_ids = self._context.get('active_ids', []) or []
        production = production_obj.browse(active_ids)
        for prod in production:
            if prod.state not in ('confirmed', 'planned', 'done'):
                continue

            for picking in prod.picking_raw_material_ids:
                if picking.state in ('draft', 'cancel', 'done'):
                    continue

                if not self.include_rm and picking.location_id.type_stock_loc == 'rm':
                    continue
                if not self.include_wip and picking.location_id.type_stock_loc != 'rm':
                    continue

                move_to_done = []
                for move in picking.move_ids_without_package.filtered(
                        lambda x: x.state in (
                            'draft', 'waiting', 'confirmed', 'assigned')):
                    move_raw_material = move.move_dest_ids.filtered(
                        lambda x: x.raw_material_production_id.id == prod.id)

                    if not move_raw_material:
                        continue

                    move.quantity_done = sum(
                        move_raw_material.mapped('product_uom_qty'))
                    move.write({'state': 'assigned'})
                    if not move.price_unit:
                        move.write({
                            'price_unit': move.product_id.standard_price})
                    move_to_done.append(move.id)

                move_obj.browse(move_to_done)._action_done()

                if not picking.date_done:
                    picking.write({'date_done': time.strftime(
                        DEFAULT_SERVER_DATETIME_FORMAT)})
            self.env.cr.commit()
