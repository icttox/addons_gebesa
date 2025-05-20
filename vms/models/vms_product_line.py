# -*- coding: utf-8 -*-
# Copyright 2016, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, exceptions, api, fields, models


class VmsProductLine(models.Model):
    _description = 'VMS Product Lines'
    _name = 'vms.product.line'

    product_id = fields.Many2one(
        'product.product',
        domain=[('type', 'in', ('product', 'consu'))],
        required=True,
        string='Spare Part')
    product_qty = fields.Float(
        required=True,
        default=0.0,
        string='Quantity',
    )
    product_uom_id = fields.Many2one(
        'uom.uom',
        string='Unit of Measure',
        required=True,
    )
    task_id = fields.Many2one(
        'vms.task',
        string='Task',
    )
    stock_location_id = fields.Many2one(
        'stock.location',
        required=True,
        string='Stock Location')
    order_line_id = fields.Many2one(
        'vms.order.line',
        string='Activity')
    state = fields.Selection(
        [('draft', 'Draft'),
         ('pending', 'Pending'),
         ('delievered', 'Delievered'),
         ('cancel', 'Cancel')],
        readonly=True, default='draft')
    name = fields.Char(
        related='task_id.name',
        string="Task"
    )

    extra_piece = fields.Boolean(
        string="Extra Piece")

    reason_extra_piece = fields.Text(
        string="Reason Extra Piece")

    @api.onchange('product_id')
    def _onchange_product_id(self):
        self.product_uom_id = self.product_id.uom_id

    @api.onchange('reason_extra_piece')
    def _onchange_extra_piece(self):
        if self.reason_extra_piece:
            self.extra_piece = True
        else:
            self.extra_piece = False

    @api.multi
    def _create_stock_picking(self):
        pick = []
        picking_dest_locations = []
        operating_units = []
        locations = self.mapped('stock_location_id')
        task_id = False
        for loc in locations:
            moves = []
            lines = self.filtered(lambda sl: sl.stock_location_id.id == loc.id)
            for rec in lines:
                today = fields.Datetime.now()
                move = (0, 0, {
                    'company_id': self.env.user.company_id.id,
                    'date': today,
                    'location_dest_id': (
                        rec.product_id.property_stock_production.id),
                    'location_id': loc.id,
                    'name': (
                        rec.order_line_id.task_id.name +
                        '-' + rec.product_id.name),
                    'product_id': rec.product_id.id,
                    'product_uom': rec.product_uom_id.id,
                    'product_uom_qty': rec.product_qty,
                    'operating_unit_id': (
                        rec.order_line_id.order_id.operating_unit_id.id),
                    'operating_unit_dest_id': (
                        rec.order_line_id.order_id.operating_unit_id.id),
                })
                # picking_locations.append(loc.id)
                picking_dest_locations.append(
                    rec.product_id.property_stock_production.id)
                operating_units.append(
                    rec.order_line_id.order_id.operating_unit_id.id)
                moves.append(move)
                task_id = rec.order_line_id.id

            # if len(set(picking_locations)) > 1:
            #     raise exceptions.ValidationError(_(
            #         'All the source locations must be equal.'))
            # if len(set(picking_dest_locations)) > 1:
            #     raise exceptions.ValidationError(_(
            #         'All the destionation locations must be equal.'))
            if len(set(operating_units)) > 1:
                raise exceptions.ValidationError(_(
                    'All the operating units must be equal.'))
            # if not self.env.user.employee_ids.default_warehouse_id:
                # raise exceptions.ValidationError(_(
                    # 'You do not have a warehouse assigned, please check with the system administrator.'))
            picking = {
                'company_id': self.env.user.company_id.id,
                'move_ids_without_package': [x for x in moves],
                'picking_type_id': loc.stock_warehouse_id.int_type_id.id,
                'location_id': loc.id,
                'location_dest_id': picking_dest_locations[0],
                'operating_unit_id': operating_units[0],
                'vms_order_line': task_id,
            }
            pick.append((4, self.env['stock.picking'].create(picking).id))
        return pick
