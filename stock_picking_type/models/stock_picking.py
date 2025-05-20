# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    stock_move_type_id = fields.Many2one(
        'stock.move.type',
        string='Type of move',
        compute='_compute_stock_move_type_id',
        store=True,
    )

    @api.onchange('stock_move_type_id',)
    def _onchange_stock_move_type_id(self):
        if self.stock_move_type_id.code in ('E4', 'S4'):
            if self.stock_move_type_id.code == 'E4':
                self.picking_type_id = self.env.user.employee_ids.\
                    default_warehouse_id.in_type_id.id
            else:
                self.picking_type_id = self.env.user.employee_ids.\
                    default_warehouse_id.out_type_id.id

    @api.depends('location_id', 'location_dest_id')
    def _compute_stock_move_type_id(self):
        move_type = None
        for picking in self:
            if picking.location_id.usage == 'customer':
                move_type = 'E1'
            elif picking.location_id.usage == 'supplier':
                move_type = 'E2'
            elif picking.location_dest_id.usage == 'customer':
                move_type = 'S1'
            elif picking.location_dest_id.usage == 'supplier':
                move_type = 'S2'
            elif picking.location_id.usage == 'transit':
                move_type = 'E3'
            elif picking.location_dest_id.usage == 'transit':
                move_type = 'S3'
            elif picking.location_id.usage == 'inventory':
                move_type = 'E4'
            elif picking.location_dest_id.usage == 'inventory':
                move_type = 'S4'
            elif picking.location_id.usage == 'internal' and \
                    picking.location_dest_id.usage == 'production':
                move_type = 'E5'
            elif picking.location_id.usage == 'production' and \
                    picking.location_dest_id.usage == 'internal':
                move_type = 'S5'

            stock_type = self.env['stock.move.type'].search([(
                'code', '=', move_type)])
            if stock_type:
                picking.stock_move_type_id = stock_type.id
