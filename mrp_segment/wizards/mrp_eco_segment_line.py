# Copyright 2024, Samuel Barron
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError


class MrpEcoSegmentLine(models.TransientModel):
    _name = 'mrp.eco.segment.line'
    _description = 'Create an engineering change order from the segment line'

    bom_id = fields.Many2one(
        'mrp.bom',
        string='Bom',
    )
    bom_products_ids = fields.Many2many(
        'product.product',
        string='Productos'
    )

    product_id = fields.Many2one(
        'product.product',
        string='Producto',
    )
    change_product = fields.Boolean(
        string='Cambiar Producto',
    )
    new_product_id = fields.Many2one(
        'product.product',
        string='Nuevo producto',
    )
    change_qty = fields.Boolean(
        string='Cambiar Cantidad',
    )
    new_qty = fields.Float(
        string='Nueva Cantidad',
        digits=dp.get_precision('Product Unit of Measure'),
    )
    create_adjustment = fields.Boolean(
        string='Crear Ajuste de inventario',
    )
    location_id = fields.Many2one(
        'stock.location',
        string='Ubicación de ajuste',
    )
    qty_adjustment1 = fields.Float(
        string='Cantidad de ajuste',
        digits=dp.get_precision('Product Unit of Measure'),
    )
    type_adjustment1 = fields.Selection(
        [('entrada', 'Entrada'),
         ('salida', 'Salida')],
        string='Tipo de ajuste',
    )
    qty_adjustment2 = fields.Float(
        string='Cantidad de ajuste',
        digits=dp.get_precision('Product Unit of Measure'),
    )

    @api.onchange('change_product', 'change_qty')
    def onchange_lines_ids(self):
        for rec in self:
            if rec.change_product is False and rec.change_qty is False:
                rec.create_adjustment = False

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        res_ids = self._context.get('active_ids')
        line = self.env['mrp.segment.line'].search([('id', '=', res_ids[0])])
        bom_id = line.mrp_production_id.bom_id
        res.update({
            'bom_id': bom_id.id,
            'bom_products_ids': bom_id.bom_line_ids.mapped('product_id').mapped('id')})
        return res

    def create_eco_change(self, eco, type, product_id, qty):
        self.env['mrp.eco.bom.change.user'].create({
            'change_type': type,
            'product_id': product_id.id,
            'new_product_qty': qty,
            'eco_id': eco.id
        })

    def create_picking(self, eco, move_type_id, picking_type, location_id, location_dest_id, adjustment_id):
        picking_id = self.env['stock.picking'].create({
            'origin': 'ECO(' + str(eco.id) + ')',
            'date': fields.Datetime.now(),
            'state': 'waiting',
            'move_type': 'direct',
            'note': eco.name,
            'company_id': self.bom_id.company_id.id,
            'stock_move_type_id': move_type_id,
            'location_id': location_id,
            'location_dest_id': location_dest_id,
            'picking_type_id': picking_type,
            'type_adjustment_id': adjustment_id,
            'authorized': True
        })

        return picking_id

    def create_move(self, eco, picking_id, product_id, qty, location_id, location_dest_id, move_type_id):
        self.env['stock.move'].create({
            'name': 'ECO(' + str(eco.id) + ')' + product_id.default_code,
            'picking_id': picking_id.id,
            'product_id': product_id.id,
            'date': fields.Datetime.now(),
            'date_expected': fields.Datetime.now(),
            'product_uom_qty': qty,
            'product_uom': product_id.uom_id.id,
            'product_packaging': False,
            'location_id': location_id,
            'location_dest_id': location_dest_id,
            'company_id': self.bom_id.company_id.id,
            'price_unit': product_id.standard_price,
            'stock_move_type_id': move_type_id,
            'quantity_done': qty,
        })

    def create_eco(self):
        if not self.change_product and not self.change_qty:
            raise UserError(
                'Debe cambiar el producto o la cantidad del producto')
        type_id = self.env.ref('mrp_plm_gebesa.ecotype2')
        state_id = self.env.ref('mrp_plm_gebesa.ecostage_new')
        line_id = self.bom_id.bom_line_ids.filtered(lambda x: x.product_id == self.product_id)

        eco = False
        ecos = self.env['mrp.eco'].search([
            ('type_id', '=', type_id.id),
            ('type', '=', 'bom'),
            ('product_id', '=', self.bom_id.product_id.id)])
        for rec in ecos.filtered(lambda x: not x.stage_id.final_stage):
            if self.product_id.id in rec.bom_user_change_ids.mapped('product_id').mapped('id'):
                eco = rec
        # import ipdb; ipdb.set_trace()
        if not eco:
            eco = self.env['mrp.eco'].create({
                'name': type_id.name + ' ' + self.bom_id.product_id.default_code,
                'type_id': type_id.id,
                'type': 'bom',
                'bom_id': self.bom_id.id,
                'product_id': self.bom_id.product_id.id,
                'product_tmpl_id': self.bom_id.product_tmpl_id.id,
                'stage_id': state_id.id,
            })

            if self.change_product:
                qty = line_id.product_qty
                self.create_eco_change(eco, 'remove', self.product_id, qty)

                if self.change_qty:
                    qty = self.new_qty
                self.create_eco_change(eco, 'add', self.new_product_id, qty)

            elif self.change_qty:
                self.create_eco_change(eco, 'update', self.product_id, self.new_qty)

        ctx = self._context.copy()
        ctx.update({'picking_merge': False})
        inv_lost = self.env.ref('stock.location_inventory')
        in_adjustment = self.env['type.adjustment'].search([('consecutive', '=', '00020')])
        out_adjustment = self.env['type.adjustment'].search([('consecutive', '=', '00021')])
        if self.create_adjustment and self.change_product:
            picking_type = self.bom_id.warehouse_id.int_type_id.id
            if self.qty_adjustment1 > 0.00:
                move_type_id = self.env['stock.move.type'].search([('code', '=', 'E4')])

                picking_id = self.create_picking(
                    eco, move_type_id[0].id, picking_type,
                    inv_lost.id, self.location_id.id, in_adjustment.id)

                self.create_move(
                    eco, picking_id, self.product_id, self.qty_adjustment1,
                    inv_lost.id, self.location_id.id,
                    move_type_id[0].id)

                picking_id.with_context(ctx).action_confirm()
                for line in picking_id.move_lines:
                    line.qty_done = line.product_uom_qty
                picking_id.button_validate()

            if self.qty_adjustment2 > 0.00:
                move_type_id = self.env['stock.move.type'].search([('code', '=', 'S4')])
                picking_id = self.create_picking(
                    eco, move_type_id[0].id, picking_type, self.location_id.id,
                    inv_lost.id, out_adjustment.id)

                self.create_move(
                    eco, picking_id, self.new_product_id, self.qty_adjustment2,
                    self.location_id.id, inv_lost.id,
                    move_type_id[0].id)

                picking_id.with_context(ctx).action_confirm()
                for line in picking_id.move_lines:
                    line.qty_done = line.product_uom_qty
                picking_id.button_validate()

        elif self.create_adjustment and self.change_qty and self.qty_adjustment1 > 0.00 and self.type_adjustment1:
            picking_type = self.bom_id.warehouse_id.int_type_id.id

            if self.type_adjustment1 == 'entrada':
                location_id = inv_lost.id
                location_dest_id = self.location_id.id
                move_type_id = self.env['stock.move.type'].search([('code', '=', 'E4')])
                adjustment = in_adjustment.id
            else:
                location_id = self.location_id.id
                location_dest_id = inv_lost.id
                move_type_id = self.env['stock.move.type'].search([('code', '=', 'S4')])
                adjustment = out_adjustment.id

            picking_id = self.create_picking(
                eco, move_type_id[0].id, picking_type,
                location_id, location_dest_id, adjustment)

            self.create_move(
                eco, picking_id, self.product_id, self.qty_adjustment1,
                location_id, location_dest_id, move_type_id[0].id)

            picking_id.with_context(ctx).action_confirm()
            for line in picking_id.move_lines:
                line.qty_done = line.product_uom_qty
            picking_id.button_validate()
