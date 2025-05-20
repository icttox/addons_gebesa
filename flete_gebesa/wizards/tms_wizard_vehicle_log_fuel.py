# # -*- coding: utf-8 -*-
# # Copyright 2012, Israel Cruz Argil, Argil Consulting
# # Copyright 2016, Jarsa Sistemas, S.A. de C.V.
# # License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

# from odoo import _, api, fields, models
# from odoo.exceptions import ValidationError, UserError
# import datetime


# class TmsWizardVehicleLogFuel(models.TransientModel):
#     _name = 'tms.wizard.vehicle.log.fuel'

#     vehicle_id = fields.Many2one(
#         'fleet.vehicle',
#         string=_('Vehicle'),
#     )
#     travel_ids = fields.Many2many(
#         'tms.travel',
#         string=_('Travels'),
#     )
#     route_id = fields.Many2one(
#         'tms.route',
#         string=_('Route'),
#     )
#     liters = fields.Float(
#         string=_('Liters'),
#     )
#     full_tank = fields.Boolean(
#         string=_('Full tank'),
#     )
#     observations = fields.Text(
#         string=_('Observations'),
#     )

#     # @api.onchange('travel_id')
#     # def _onchange_travel(self):
#     #     self.vehicle_id = self.travel_id.unit_id

#     @api.onchange('vehicle_id')
#     def _onchange_vehicle_id(self):
#         self.travel_ids = None

#     @api.multi
#     def create_fleet_vehicle_log_fuel(self):
#         # import ipdb; ipdb.set_trace()
#         if self.liters < 0.0:
#             raise ValidationError(
#                 _('Los litros tienen que ser mayor o igual a 0'))

#         # fleet_vehicle = self.env['fleet.vehicle.log.fuel']
#         warehouse_obj = self.env['stock.warehouse']
#         picking = self.env['stock.picking']
#         move = self.env['stock.move']
#         product = self.env['ir.values'].get_default(
#             'tms.config.settings', 'product_id')
#         location = self.env['ir.values'].get_default(
#             'tms.config.settings', 'location_id')
#         location_dest = self.env['ir.values'].get_default(
#             'tms.config.settings', 'location_dest_id')
#         type_adjustment = self.env['ir.values'].get_default(
#             'tms.config.settings', 'type_adjustment_id')
#         move_type_obj = self.env['stock.move.type']
#         move_type_id = move_type_obj.search([('code', '=', 'S4')])
#         users = self.env.user
#         product_obj = self.env['product.product']
#         warehouse = warehouse_obj.search([], limit=1)

#         for fleets in self:
#             # if fleets.travel_id:
#             #     fleets.vehicle_id = fleets.travel_id.unit_id
#             if not product:
#                 raise UserError(_('You do not have the product configured for diesel.'))
#             if not location and not location_dest and not type_adjustment:
#                 raise UserError(_('The fields are not configured'))
#             product = product_obj.browse([product])


#             # fleet_fields = {
#             #     'operating_unit_id': users.default_operating_unit_id.id,
#             #     'vendor_id': users.company_id.partner_id.id,
#             #     'product_id': product.id,
#             #     'travel_id': fleets.travel_id.id,
#             #     'currency_id': users.company_id.currency_id.id,
#             #     'vehicle_id': fleets.vehicle_id.id,
#             #     'product_qty': fleets.liters,
#             #     'tax_amount': 0,
#             #     'price_total': product.standard_price * fleets.liters
#             # }
#             # log_fuel = fleet_vehicle.create(fleet_fields)
#             # log_fuel.action_approved()
#             # log_fuel.action_confirm()

#             origin = ''
#             kilometer = 0
#             if fleets.travel_ids:
#                 employee_id = fleets.mapped('travel_ids').mapped(
#                     'employee_id').mapped('id')
#                 if len(employee_id) > 1:
#                     raise UserError(_('Error chofer'))

#                 unit_id = fleets.mapped('travel_ids').mapped(
#                     'unit_id').mapped('id')
#                 if len(unit_id) > 1:
#                     raise UserError(_('Error varios camiones'))
#                 if unit_id[0] != fleets.vehicle_id.id:
#                     raise UserError(_('Error camiones diferentes'))
#                 for travel in fleets.travel_ids:
#                     origin += travel.name + '-'
#                     kilometer += travel.distance_route
#             origin += product.name + ' - ' + str(fleets.liters)

#             stock_picking_ = {
#                 'origin': origin,
#                 'date': datetime.date.today(),
#                 'type': 'out',
#                 'state': 'waiting',
#                 'move_type': 'direct',
#                 'partner_id': users.company_id.partner_id.id,
#                 'company_id': users.company_id.id,
#                 'stock_move_type_id': move_type_id[0].id,
#                 'location_id': location,
#                 'location_dest_id': location_dest,
#                 'type_adjustment_id': type_adjustment,
#                 'picking_type_id': warehouse.out_type_id.id,
#                 'authorized': True,
#                 'vehicle_id': fleets.vehicle_id.id,
#                 'route_id': fleets.route_id.id,
#                 'travel_ids': [(6, 0, fleets.travel_ids.ids)],
#                 'full_tank': fleets.full_tank,
#                 'note': fleets.observations,
#                 'driver_id': employee_id[0],
#                 'kilometer': kilometer
#             }
#             stock_picking = picking.create(stock_picking_)

#             stock_move_ = {
#                 'name': origin,
#                 'picking_id': stock_picking.id,
#                 'product_id': product.id,
#                 'date': datetime.date.today(),
#                 'date_expected': datetime.date.today(),
#                 'product_uom_qty': fleets.liters,
#                 'product_uom': product.uom_id.id,
#                 'product_uos_qty': fleets.liters,
#                 'product_uos': product.uom_id.id,
#                 'product_packaging': False,
#                 'partner_id': users.company_id.partner_id.id,
#                 'location_id': location,
#                 'location_dest_id': location_dest,
#                 'tracking_id': False,
#                 'company_id': users.company_id.id,
#                 'price_unit': product.standard_price,
#                 'stock_move_type_id': move_type_id[0].id
#             }
#             stock_move = move.create(stock_move_)
#             # log_fuel.write({'picking_id': stock_picking.id})

#             # if stock_picking.state == 'draft':
#             #     stock_picking.action_confirm()
#             #     if stock_picking.state != 'assigned':
#             #         stock_picking.action_assign()
#             #         if stock_picking.state != 'assigned':
#             #             raise UserError(_("Could not reserve all requested products. Please use the \'Mark as Todo\' button to handle the reservation manually."))
#             # for pack in stock_picking.pack_operation_ids:
#             #     if pack.product_qty > 0:
#             #         pack.write({'qty_done': pack.product_qty})
#             #     else:
#             #         pack.unlink()
#             # ctx = self._context.copy()
#             # ctx.update({
#             #     'force_vehicle_analytic_id': fleets.vehicle_id.account_analytic_id.id})
#             # stock_picking.with_context(ctx).do_transfer()

#             # return {
#             #     'type': 'ir.actions.act_window',
#             #     'res_model': 'fleet.vehicle.log.fuel',
#             #     'view_mode': 'form',
#             #     'view_type': 'form',
#             #     'res_id': log_fuel.id,
#             #     'views': [(False, 'form')],
#             # }
#             return {
#                 'type': 'ir.actions.act_window',
#                 'res_model': 'stock.picking',
#                 'view_mode': 'form',
#                 'view_type': 'form',
#                 'res_id': stock_picking.id,
#                 'views': [(False, 'form')],
#             }
