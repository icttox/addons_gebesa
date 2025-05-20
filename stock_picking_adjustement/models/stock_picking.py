# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    type_adjustment_id = fields.Many2one('type.adjustment',
                                         string='Type Adjustment',
                                         store=True,)

    adjustment_responsible = fields.Char(
        string='Responsible',
    )

    adj_reason = fields.Char(
        string='Reason',
    )

    adj_class = fields.Char(
        string='Classification',
    )

    total_cost = fields.Float(
        string='Totals Cost',
        compute="compute_total_cost"
    )

    @api.model
    def create(self, vals_list):
        res = super().create(vals_list)

        if self.type_adjustment_id and self.company_id.is_manufacturer:
            if self.location_id.usage == 'internal' and self.location_dest_id.usage == 'inventory' and type_adjustment_id.type_adjustment != 'output':
                raise ValidationError(
                    _('No coincide el tipo de ajuste (salida) con los datos del movimiento Favor de verificar'))

            if self.location_id.usage == 'inventory' and self.location_dest_id.usage == 'internal' and type_adjustment_id.type_adjustment != 'input':
                raise ValidationError(
                    _('No coincide el tipo de ajuste (entrada) con los datos del movimiento Favor de verificar'))

        return res


    @api.onchange('picking_type_id', 'partner_id')
    def onchange_picking_type(self):
        super().onchange_picking_type()
        location_dest = self.env.context.get('default_location_dest_id') or False
        location = self.env.context.get('default_location_id') or False
        if self.state == 'draft':
            if location_dest:
                self.location_dest_id = location_dest
            if location:
                self.location_id = location

    @api.depends('move_ids_without_package', 'move_ids_without_package.product_id',
                 'move_ids_without_package.product_uom_qty', 'move_ids_without_package.state')
    def compute_total_cost(self):
        for picking in self:
            picking.total_cost = 0.0
            for move in picking.move_ids_without_package:
                # import ipdb; ipdb.set_trace()
                if move.state != 'cancel':
                    price = move.price_unit
                    if price == 0:
                        price = move.product_id.standard_price

                    picking.total_cost += abs(
                        move.product_uom_qty * price)

    @api.multi
    def dynamic_action_adjustment_output(self):
        inventory_lost = self.env['stock.location'].search(
            [('usage', '=', 'inventory')], limit=1)
        ctx = self._context.copy()
        ctx['default_stock_move_type_id'] = self.env.ref(
            'stock_picking_type.mpf_tipomov_S4').id
        ctx['default_location_dest_id'] = inventory_lost.id
        ctx['default_picking_type_id'] = self.env.user.employee_ids.default_warehouse_id.out_type_id.id
        action = {
            'type': "ir.actions.act_window",
            'name': _('Adjustment OutPut'),
            'res_model': "stock.picking",
            'view_type': "form",
            'view_mode': "tree,form",
            'domain': "[('stock_move_type_id.code', 'in', ['S4']), \
                        ('picking_type_id.code', '=', 'outgoing'), \
                        ('picking_type_id.warehouse_id', '!=', False)]",
            'context': ctx,
        }
        return action

    @api.multi
    def dynamic_action_adjustment_input(self):
        inventory_lost = self.env['stock.location'].search(
            [('usage', '=', 'inventory')], limit=1)
        ctx = self._context.copy()
        ctx['default_stock_move_type_id'] = self.env.ref(
            'stock_picking_type.mpf_tipomov_E4').id
        ctx['default_location_id'] = inventory_lost.id
        ctx['default_picking_type_id'] = self.env.user.employee_ids.default_warehouse_id.in_type_id.id
        action = {
            'type': "ir.actions.act_window",
            'name': _('Adjustment Input'),
            'res_model': "stock.picking",
            'view_type': "form",
            'view_mode': "tree,form",
            'domain': "[('stock_move_type_id.code', 'in', ['E4']), \
                        ('picking_type_id.code', '=', 'incoming'), \
                        ('picking_type_id.warehouse_id', '!=', False)]",
            'context': ctx
        }
        return action
