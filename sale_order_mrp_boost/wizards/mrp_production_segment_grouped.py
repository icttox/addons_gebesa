# Copyright 2024, Marco Esquivel
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError


class AttendanceReportsWizard(models.TransientModel):
    _name = 'mrp.production.segment.grouped'
    _description = 'Wizard para agrupar Mo dependiendo del segmento y la ubicacion'

    segment_id = fields.Many2one(
        'mrp.segment',
        string='Segment',
    )

    location_id = fields.Many2one(
        'stock.location',
        string='Ubication',
    )

    mo_grouped = fields.One2many(
        'production.mo.grouped',
        'production_segment_id',
        string='Grouped mo',
    )

    visibility = fields.Boolean(
        string='Visibility',
        default=False
    )

    percentage = fields.Integer(
        string='Percentage',
        default=100,
    )

    def get_mo_produced(self):
        segment = self.segment_id

        product_info_list = []

        quantity_done = 0

        for picking in segment.picking_ids.filtered(lambda p: p.state == 'done'):
            for move in picking.move_ids_without_package.filtered(lambda m: m.state == 'done'):
                product_id = move.product_id.id
                quantity_done = move.product_uom_qty

                existing_product = next((item for item in product_info_list if item['product_id'] == product_id), None)

                if existing_product:
                    existing_product['delivered_quantity'] += quantity_done
                else:
                    product_info_list.append({
                        'product_id': product_id,
                        'quantity_pending': 0,
                        'quantity': 0,
                        'production_segment_id': self.id,
                        'delivered_quantity': quantity_done,
                        'total_quantity': 0,
                    })

        for production in segment.line_ids.filtered(lambda x: x.state in ['progress', 'confirmed', 'planned']).mapped('mrp_production_id').filtered(lambda p: not p.picking_raw_material_ids and not p.picking_move_prod_ids):
            for move_raw1 in production.move_raw_ids.filtered(lambda x: x.state not in ['cancel', 'draft']):
                product_id = move_raw1.product_id.id
                total_quantity = move_raw1.product_uom_qty

                existing_product = next((item for item in product_info_list if item['product_id'] == product_id), None)

                if existing_product:
                    existing_product['total_quantity'] += total_quantity
                    existing_product['quantity_pending'] = existing_product['total_quantity'] - existing_product['delivered_quantity']

                else:
                    product_info_list.append({
                        'product_id': product_id,
                        'total_quantity': total_quantity,
                        'quantity_pending': total_quantity,
                        'quantity': 0,
                        'production_segment_id': self.id,
                        'delivered_quantity': 0,
                    })

        self.env['production.mo.grouped'].create(product_info_list)
        self.visibility = True

        return {
            'name': 'Abastecer segmento',
            'type': 'ir.actions.act_window',
            'res_model': 'mrp.production.segment.grouped',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def quantity_percentage(self):
        for record in self.mo_grouped:
            record.quantity = (self.percentage / 100.0) * record.quantity_pending

            record.write({'quantity': record.quantity})

        return {
            'name': 'Abastecer segmento',
            'view_mode': 'form',
            'res_model': self._name,
            'res_id': self.id,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    @api.multi
    def action_confirm(self):
        picking_obj = self.env['stock.picking']
        move_obj = self.env['stock.move']
        warehouse_obj = self.env['stock.warehouse']
        move_type_obj = self.env['stock.move.type']
        move_type_id = move_type_obj.search([('code', '=', 'E3')]) or False

        location = self.location_id
        location_dest = self.segment_id.location_id
        users = self.env.user
        warehouse = warehouse_obj.search([('id', '=', location.stock_warehouse_id.id)], limit=1)

        origin = 'Produce - ' + self.segment_id.folio

        picking_vals = {
            'origin': origin,
            'date': fields.Date.context_today(self),
            'type': 'out',
            'state': 'waiting',
            'move_type': 'direct',
            'company_id': users.company_id.id,
            'location_id': location.id,
            'location_dest_id': location_dest.id,
            'picking_type_id': warehouse.int_type_id.id,
            'authorized': True,
            'operating_unit_id': warehouse.operating_unit_id.id,
            'segment_id': self.segment_id.id,
            'review': 'yes_review',
            'stock_move_type_id': move_type_id[0].id,
        }

        picking = picking_obj.create(picking_vals)

        for rec in self.mo_grouped:
            if rec.quantity <= 0:
                continue

            if rec.quantity > rec.quantity_pending:
                raise ValidationError('The quantity to be delivered cannot be greater than the quantity available for the product %s' % rec.product_id.name)

            if rec.product_id.type == 'product':
                product = rec.product_id
                if not location and not location_dest:
                    raise UserError('The fields are not configured')

                stock_move_ = {
                    'name': origin,
                    'picking_id': picking.id,
                    'product_id': product.id,
                    'date': fields.Date.context_today(self),
                    'date_expected': fields.Date.context_today(self),
                    'product_uom_qty': rec.quantity,
                    'product_uom': product.uom_id.id,
                    'product_packaging': False,
                    'location_id': location.id,
                    'location_dest_id': location_dest.id,
                    'company_id': users.company_id.id,
                    'price_unit': product.standard_price,
                    'stock_move_type_id': move_type_id[0].id,
                }

                move_obj.create(stock_move_)

        picking.action_confirm()
        picking.force_assign()
        picking.button_validate()
