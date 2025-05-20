# -*- coding: utf-8 -*-
# © <2016> <César Barrón Butista>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_round


class MrpProductProduce(models.TransientModel):
    _inherit = "mrp.product.produce"

    @api.multi
    def do_produce(self):
        res = super().do_produce()
        self.production_id.post_inventory()
        qty_produce = sum(self.production_id.move_finished_ids.filtered(
            lambda x: x.state == 'done').mapped('product_uom_qty'))
        if self.production_id.company_id.skip_handover_mo:
            qty_transfer = sum(self.production_id.move_dest_ids.filtered(
                lambda x: x.state == 'done').mapped('product_uom_qty'))
            if qty_produce > qty_transfer:
                qty_for_transfer = qty_produce - qty_transfer
                for move in self.production_id.move_dest_ids.filtered(
                        lambda x: x.state not in ('done', 'cancel')):
                    if qty_for_transfer > 0:
                        if move.product_uom_qty >= qty_for_transfer:
                            move.write({
                                'quantity_done': qty_for_transfer,
                                'state': 'assigned'})
                            qty_for_transfer -= qty_for_transfer
                        else:
                            move.write({
                                'quantity_done': move.product_uom_qty,
                                'state': 'assigned'})
                            qty_for_transfer -= move.product_uom_qty
                        move._action_done()
                    if not move.picking_id.date_done:
                        move.picking_id.write({'date_done': fields.Datetime.now()})
        if self.production_id.product_qty == qty_produce:
            self.production_id.button_mark_done()
        return res

    @api.onchange('product_qty')
    def _onchange_product_qty(self):
        lines = []
        qty_todo = self.product_uom_id._compute_quantity(
            self.product_qty, self.production_id.product_uom_id, round=False)
        for move in self.production_id.move_raw_ids.filtered(
                lambda m: m.state not in ('done', 'cancel')):
            qty_to_consume = float_round(
                qty_todo * move.unit_factor,
                precision_rounding=move.product_uom.rounding)
            for move_line in move.move_line_ids:
                if float_compare(
                        qty_to_consume, 0.0,
                        precision_rounding=move.product_uom.rounding) <= 0:
                    break
                if move_line.lot_produced_id or float_compare(
                        move_line.product_uom_qty, move_line.qty_done,
                        precision_rounding=move.product_uom.rounding) <= 0:
                    continue
                to_consume_in_line = min(
                    qty_to_consume, move_line.product_uom_qty)
                lines.append({
                    'move_id': move.id,
                    'qty_to_consume': to_consume_in_line,
                    'qty_done': to_consume_in_line,
                    'lot_id': move_line.lot_id.id,
                    'product_uom_id': move.product_uom.id,
                    'product_id': move.product_id.id,
                    'qty_reserved': min(to_consume_in_line,
                                        move_line.product_uom_qty),
                })
                qty_to_consume -= to_consume_in_line
            if float_compare(
                    qty_to_consume, 0.0,
                    precision_rounding=move.product_uom.rounding) > 0:
                if move.product_id.tracking == 'serial':
                    while float_compare(
                            qty_to_consume, 0.0,
                            precision_rounding=move.product_uom.rounding) > 0:
                        lines.append({
                            'move_id': move.id,
                            'qty_to_consume': 1,
                            'qty_done': 1,
                            'product_uom_id': move.product_uom.id,
                            'product_id': move.product_id.id,
                        })
                        qty_to_consume -= 1
                else:
                    lines.append({
                        'move_id': move.id,
                        'qty_to_consume': qty_to_consume,
                        'qty_done': qty_to_consume,
                        'product_uom_id': move.product_uom.id,
                        'product_id': move.product_id.id,
                    })

        self.produce_line_ids = [(5,)] + [(0, 0, x) for x in lines]


class MrpProduction(models.Model):
    _name = 'mrp.production'
    _inherit = 'mrp.production'

    # procurement_ids = fields.One2many(
    #     'procurement.order',
    #     'production_id',
    #     string='Procurement',
    # )
    # trace = fields.Char(
    #     string='Trace',
    #     compute='_compute_trace',
    #     store=True,
    # )
    approved_to_produce = fields.Boolean(
        string='Approved to produce',
    )
    picking_raw_material_ids = fields.Many2many(
        'stock.picking',
        string='Picking Raw Material',
        compute='_compute_picking_raw_material_ids',
    )
    picking_move_prod_id = fields.Many2one(
        'stock.picking',
        string='Picking Production',
        # compute='_compute_picking_move_prod_id',
        # store=True,
    )
    picking_move_prod_ids = fields.Many2many(
        'stock.picking',
        string='Picking Production',
        compute='_compute_picking_move_prod_ids',
    )
    cancellation_reason = fields.Text(
        string='Cancellation reason',
    )

    transfer_status = fields.Selection(
        [('not_transferred', 'Not transferred'),
         ('transferred', 'Transferred')],
        string="Transfer status",
        compute='_compute_transfer_status',
        # store=True,
    )

    state = fields.Selection(
        selection_add=[
            ('transfer', 'Traspasado'),
            ('draft', 'Draft'),
        ],
    )
    rule_id = fields.Many2one(
        'stock.rule',
        'stock Rule',
        ondelete='restrict',
        help='The stock rule that created this production'
    )

    @api.depends('move_raw_ids', 'move_dest_ids')
    def _compute_picking_ids(self):
        for order in self:
            if order.state == 'cancel':
                order.picking_ids = self.env['stock.picking'].search([
                    ('group_id', '=', order.procurement_group_id.id),
                    ('group_id', '!=', False),
                ])
            else:
                picking = order.move_dest_ids.filtered(
                    lambda rec: rec.picking_id).mapped('picking_id').ids
                procurement_move = self.env['stock.move'].search(
                    [('move_dest_ids', 'in', order.move_raw_ids.mapped('id'))])
                picking.extend(procurement_move.filtered(
                    lambda rec: rec.picking_id).mapped('picking_id').ids)
                order.picking_ids = self.env['stock.picking'].browse(picking)
            order.delivery_count = len(order.picking_ids)

    @api.multi
    def _generate_moves(self):
        prod_gen = self.filtered(lambda prod: prod.procurement_group_id.sale_id)
        for production in self.filtered(lambda prod: not prod.procurement_group_id.sale_id):
            if production.approved_to_produce:
                prod_gen += production
            else:
                production.write({'state': 'draft'})
        return super(MrpProduction, prod_gen)._generate_moves()

    @api.multi
    def action_confirm(self):
        prod_gen = self.env['mrp.production']
        for production in self:
            if production.state == 'draft':
                production.write({
                    'state': 'confirmed',
                    'approved_to_produce': True})
                prod_gen += production
        prod_gen._generate_moves()

    @api.multi
    def action_view_procures(self):
        action = self.env.ref('stock.action_picking_tree_all').read()[0]
        if self.picking_raw_material_ids:
            action['domain'] = [('id', 'in', self.picking_raw_material_ids.ids)]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    @api.multi
    def action_view_transfers(self):
        action = self.env.ref('stock.action_picking_tree_all').read()[0]
        if self.picking_move_prod_ids:
            action['domain'] = [('id', 'in', self.picking_move_prod_ids.ids)]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    @api.multi
    @api.depends('workorder_ids.state', 'move_finished_ids', 'is_locked')
    def _get_produced_qty(self):
        res = super()._get_produced_qty()
        for production in self.filtered(lambda x: x.state == 'transfer'):
            production.check_to_done = False
        return res

    @api.depends('move_dest_ids')
    def _compute_picking_move_prod_ids(self):
        for prod in self:
            pickings = []
            for move in prod.move_dest_ids:
                if move.picking_id:
                    pickings.append(move.picking_id.id)
            prod.picking_move_prod_ids = pickings

    @api.depends('move_raw_ids')
    def _compute_picking_raw_material_ids(self):
        move_obj = self.env['stock.move']
        for prod in self:
            moves = prod.move_raw_ids.mapped('id')
            moves_dest = move_obj.search([('move_dest_ids', 'in', moves)])
            pickings = []
            for mov in moves_dest:
                if mov.picking_id:
                    if mov.picking_id.id not in pickings:
                        pickings.append(mov.picking_id.id)
            prod.picking_raw_material_ids = pickings

    # @api.depends(
    #     'procurement_ids',
    #     'procurement_ids.move_dest_id.picking_id',
    #     'procurement_ids.move_dest_id.move_dest_id.picking_id',
    #     'procurement_ids.move_dest_id.move_dest_id.move_dest_id.picking_id',
    #     'procurement_ids.move_dest_id.move_dest_id.move_dest_id.move_dest_id.picking_id')
    # def _compute_trace(self):
    #     return
    #     for production in self:
    #         production.trace = ''
    #         produrement = production.procurement_ids
    #         if produrement.move_dest_id:
    #             sm1 = produrement.move_dest_id
    #             if sm1.origin:
    #                 production.trace += sm1.origin + ', '
    #             if sm1.picking_id.name:
    #                 production.trace += sm1.picking_id.name
    #             if sm1.move_dest_id.picking_id:
    #                 sm2 = sm1.move_dest_id
    #                 production.trace += ', ' + sm2.picking_id.name
    #                 if sm2.move_dest_id.picking_id:
    #                     sm3 = sm2.move_dest_id
    #                     if sm3.picking_id.name:
    #                         production.trace += ', ' + sm3.picking_id.name
    #                     if sm3.move_dest_id.picking_id:
    #                         sm4 = sm3.move_dest_id
    #                         production.trace += ', ' + sm4.picking_id.name

    @api.depends('state', 'move_finished_ids',
                 'move_finished_ids.move_dest_ids',
                 'move_finished_ids.move_dest_ids.state')
    def _compute_transfer_status(self):
        for prod in self:
            transfer = True
            for move in prod.move_finished_ids:
                if move.state != 'done':
                    transfer = False
                    continue
                for move_dest in move.move_dest_ids:
                    if move_dest.state != 'done':
                        transfer = False
                        continue
            if transfer:
                prod.transfer_status = 'transferred'
                if prod.state == 'done':
                    self.env.cr.execute("""UPDATE mrp_production SET state = 'transfer'
                                        WHERE id = %s """ % (prod.id))
            else:
                prod.transfer_status = 'not_transferred'

    @api.model
    def create(self, vals_list):
        if 'bom_id' not in vals_list.keys() and 'product_id' in vals_list.keys() and 'picking_type_id' in vals_list.keys():
            bom = self.env['mrp.bom']._bom_find(
                product=self.env['product.product'].browse([vals_list['product_id']]),
                picking_type=self.env['stock.picking.type'].browse([vals_list['picking_type_id']]),
                company_id=self.env.user.company_id.id)
            if bom.type == 'normal':
                vals_list['bom_id'] = bom.id

        res = super().create(vals_list)
        for move in res.move_dest_ids:
            move.origin += ':' + res.name + ' ' + res.location_dest_id.name
            if move.picking_id:
                move.picking_id.origin = move.origin
        return res

    def _get_raw_move_data(self, bom_line, line_data):
        res = super()._get_raw_move_data(bom_line, line_data)
        if bom_line.location_id and bom_line.location_id.company_id.skip_supply_mo:
            res['location_id'] = bom_line.location_id.id
        return res

    def _generate_raw_move(self, bom_line, line_data):
        quantity = line_data['qty']
        # alt_op needed for the case when you explode phantom bom and all the lines will be consumed in the operation given by the parent bom line
        alt_op = (line_data['parent_line'].operation_id.id if line_data['parent_line'] else False)
        if bom_line.child_bom_id and bom_line.child_bom_id.type == 'phantom':
            return self.env['stock.move']
        if bom_line.product_id.type not in ['product', 'consu']:
            return self.env['stock.move']

        # Take routing location as a Source Location.
        source_location = self.location_src_id.id
        if bom_line and bom_line.location_id:
            source_location = bom_line.location_id

        original_quantity = (self.product_qty - self.qty_produced) or 1.0
        data = {
            'sequence': bom_line.sequence,
            'name': self.name,
            'date': self.date_planned_start,
            'date_expected': self.date_planned_start,
            'bom_line_id': bom_line.id,
            'product_id': bom_line.product_id.id,
            'product_uom_qty': quantity,
            'product_uom': bom_line.product_uom_id.id,
            'location_id': source_location.id,
            'location_dest_id': self.product_id.property_stock_production.id,
            'raw_material_production_id': self.id,
            'company_id': self.company_id.id,
            'operation_id': bom_line.operation_id.id or alt_op,
            'price_unit': bom_line.product_id.standard_price,
            'procure_method': 'make_to_stock',
            'origin': self.name,
            'warehouse_id': source_location.get_warehouse().id,
            'group_id': self.procurement_group_id.id,
            'propagate': self.propagate,
            'unit_factor': quantity / original_quantity,
        }
        return self.env['stock.move'].create(data)

    @api.multi
    def action_cancel(self):
        for production in self:
            if not self.env.user.has_group(
                    'system_administrator.group_system_administrator_gebesa'):
                raise UserError(_('Only Administrator can cancel'))

            if not production.cancellation_reason:
                raise UserError(_('Specify the reason for cancellation'))

        picking_raw_material_ids = self.mapped('picking_raw_material_ids')
        res = super().action_cancel()

        for picking in picking_raw_material_ids:
            if picking.state not in ['done', 'cancel']:
                picking.do_unreserve()
                moves = ''
                cancel_pick = True
                for move in picking.move_ids_without_package:
                    if move.state != 'done':
                        moves += str(move.id) + ','
                    else:
                        cancel_pick = False
                if moves != '':
                    moves = moves[:-1]
                    self.env.cr.execute("""
                        UPDATE stock_move SET state = 'cancel'
                        WHERE id in (%s) """ % (moves))
                if cancel_pick:
                    self.env.cr.execute("""
                        UPDATE stock_picking SET state = 'cancel'
                        WHERE id in (%s) """ % (picking.id))

        for picking in self.mapped('picking_move_prod_ids'):
            if picking.state not in ['done', 'cancel']:
                picking.do_unreserve()
                moves = ''
                cancel_pick = True
                for move in picking.move_ids_without_package:
                    if move.state != 'done':
                        moves += str(move.id) + ','
                    else:
                        cancel_pick = False
                if moves != '':
                    moves = moves[:-1]
                    self.env.cr.execute("""
                        UPDATE stock_move SET state = 'cancel'
                        WHERE id in (%s) """ % (moves))
                if cancel_pick:
                    self.env.cr.execute("""
                        UPDATE stock_picking SET state = 'cancel'
                        WHERE id in (%s) """ % (picking.id))

        # Cancel movelines y desreservar, para stock_moves_cancelados:
        # Asi es, no filtra solo los movimientos de este pedido, es a proposito
        # No deberian ser muchos
        self._cr.execute("""
            UPDATE stock_move_line
                SET state = 'cancel',
                product_qty = 0.00000
            FROM stock_move sm
            WHERE sm.id = stock_move_line.move_id
            AND sm.state = 'cancel' AND stock_move_line.state != 'cancel'
        """)

        return res
