# -*- coding: utf-8 -*-
# Copyright 2018, Cesar Barron
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, UserError
# import json
# import base64
_logger = logging.getLogger(__name__)

class FleetVehicleLogFuel(models.Model):
    _name = 'fleet.vehicle.log.fuel'
    _inherit = 'fleet.vehicle.log.fuel'

    km_traveled = fields.Float(
        string='Kilometers traveled',
    )
    performance_km_l = fields.Float(
        string='Performance',
        compute="_compute_performance_km_l",
    )
    hours_worked = fields.Float(
        string='Hours worked',
    )
    performance_h_l = fields.Float(
        string='Performance hours ',
        compute="_compute_performance_h_l",
    )

    dispersion_id = fields.Many2one(
        'dispersion.diesel',
        string='Dispersion',
    )

    @api.depends('km_traveled', 'product_qty')
    def _compute_performance_km_l(self):
        for log in self:
            if log.product_qty > 0.0:
                log.performance_km_l = (
                    log.km_traveled / log.product_qty)
            else:
                log.performance_km_l = 0.0

    @api.depends('hours_worked', 'product_qty')
    def _compute_performance_h_l(self):
        for log in self:
            if log.product_qty > 0.0:
                log.performance_h_l = (
                    log.hours_worked / log.product_qty)
            else:
                log.performance_h_l = 0.0

    # image_qr = fields.Binary(
    #     attachment=True,
    #     string="File QR")

    @api.multi
    @api.depends('tax_amount', 'price_total')
    def _compute_price_subtotal(self):
        for rec in self:
            rec.price_subtotal = rec.price_total
            if rec.tax_amount > 0:
                rec.price_subtotal = rec.price_total - rec.tax_amount

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_(
                    'You can only delete vouchers in draft status'))
        return super().unlink()

    @api.multi
    def action_cancel(self):
        move_type_obj = self.env['stock.move.type']
        picking_obj = self.env['stock.picking']
        move_obj = self.env['stock.move']
        warehouse_obj = self.env['stock.warehouse']
        res = super().action_cancel()
        for rec in self:
            if rec.dispersion_id and not self._context.get('cancel_from_dispersion'):
                raise UserError("No se puede cancelar un vale que viene de una dispersion")

            if rec.product_id.type == 'product':

                # location = self.env[
                #     'ir.config_parameter'].sudo().get_param(
                #         'tms.tms_location_id')
                # location_dest = self.env[
                #     'ir.config_parameter'].sudo().get_param(
                #         'tms.tms_location_dest_id')
                # type_adjustment = self.env[
                #     'ir.config_parameter'].sudo().get_param(
                #         'tms.tms_type_adjustment_id')

                location_dest = self.env.user.company_id.tms_location_id
                location = self.env.user.company_id.tms_location_dest_id
                type_adjustment = self.env.user.company_id.tms_type_adjustment_ret_id

                move_type_id = move_type_obj.search([('code', '=', 'E4')])
                users = self.env.user
                warehouse = warehouse_obj.search([], limit=1)
                product = self.product_id
                if not location and not location_dest and not type_adjustment:
                    raise UserError(_('The fields are not configured'))

                origin = _('Return ') + rec.name + '-'
                if rec.travel_id:
                    origin += rec.travel_id.name + '-'
                origin += product.name + ' - ' + str(rec.product_qty)

                picking_vals = {
                    'origin': origin,
                    'date': fields.Date.context_today(self),
                    'type': 'out',
                    'state': 'waiting',
                    'move_type': 'direct',
                    'partner_id': users.company_id.partner_id.id,
                    'company_id': users.company_id.id,
                    'stock_move_type_id': move_type_id[0].id,
                    'location_id': location.id,
                    'location_dest_id': location_dest.id,
                    'type_adjustment_id': type_adjustment.id,
                    'picking_type_id': warehouse.in_type_id.id,
                    'authorized': True,
                    'vehicle_id': rec.vehicle_id.id,
                    # 'full_tank': rec.full_tank,
                    'note': rec.notes,
                    'operating_unit_id': warehouse.operating_unit_id.id
                }
                if rec.travel_id:
                    picking_vals['travel_ids'] = [(6, 0, [rec.travel_id.id])]
                    picking_vals['route_id'] = rec.travel_id.route_id.id
                    picking_vals['driver_id'] = rec.travel_id.employee_id.id
                    picking_vals['kilometer'] = rec.travel_id.distance_route

                picking = picking_obj.create(picking_vals)

                stock_move_ = {
                    'name': origin,
                    'picking_id': picking.id,
                    'product_id': product.id,
                    'date': fields.Date.context_today(self),
                    'date_expected': fields.Date.context_today(self),
                    'product_uom_qty': rec.product_qty,
                    'product_uom': product.uom_id.id,
                    'product_uos_qty': rec.product_qty,
                    'product_uos': product.uom_id.id,
                    'product_packaging': False,
                    'partner_id': users.company_id.partner_id.id,
                    'location_id': location.id,
                    'location_dest_id': location_dest.id,
                    'tracking_id': False,
                    'company_id': users.company_id.id,
                    'price_unit': product.standard_price,
                    'stock_move_type_id': move_type_id[0].id
                }
                move_obj.create(stock_move_)
                # rec.write({'picking_id': picking.id})

                # if rec.picking_id:
                if picking.state == 'draft':
                    picking.action_confirm()
                    if picking.state != 'assigned':
                        picking.action_assign()
                        if picking.state != 'assigned':
                            raise UserError(_("Could not reserve all requested products. Please use the \'Mark as Todo\' button to handle the reservation manually."))
                if picking.state != 'done':
                    for move in picking.move_ids_without_package.filtered(lambda m: m.state not in ['done', 'cancel']):
                        for move_line in move.move_line_ids:
                            move_line.qty_done = move_line.product_uom_qty
                    ctx = self._context.copy()
                    ctx.update({
                        'force_vehicle_analytic_id': rec.vehicle_id.account_analytic_id.id})
                    picking.with_context(ctx).action_done()
        return res

    @api.multi
    def action_confirm(self):
        move_type_obj = self.env['stock.move.type']
        picking_obj = self.env['stock.picking']
        move_obj = self.env['stock.move']
        warehouse_obj = self.env['stock.warehouse']
        for rec in self:
            if (rec.product_qty <= 0 or
                    # rec.tax_amount <= 0 or
                    rec.price_total <= 0):
                raise ValidationError(
                    _('Liters and Total'
                      ' must be greater than zero.'))
            rec.message_post(body=_('<b>Fuel Voucher Confirmed.</b>'))
            rec.state = 'confirmed'
            if rec.product_id.type == 'product':
                # get_param = self.env['ir.config_parameter'].sudo().get_param
                # location = literal_eval(get_param(
                #     'tms.tms_location_id', default='False'))
                # location_dest = literal_eval(get_param(
                #     'tms.tms_location_dest_id', default='False'))
                # type_adjustment = literal_eval(get_param(
                #     'tms.tms_type_adjustment_id', default='False'))

                # location = self.env[
                #     'ir.config_parameter'].sudo().get_param(
                #         'tms.tms_location_id')
                # location_dest = self.env[
                #     'ir.config_parameter'].sudo().get_param(
                #         'tms.tms_location_dest_id')
                # type_adjustment = self.env[
                #     'ir.config_parameter'].sudo().get_param(
                #         'tms.tms_type_adjustment_id')

                location = self.env.user.company_id.tms_location_id
                location_dest = self.env.user.company_id.tms_location_dest_id
                type_adjustment = self.env.user.company_id.tms_type_adjustment_id

                move_type_id = move_type_obj.search([('code', '=', 'S4')])
                users = self.env.user
                warehouse = warehouse_obj.search([], limit=1)
                product = self.product_id
                if not location and not location_dest and not type_adjustment:
                    raise UserError(_('The fields are not configured'))

                if rec.product_qty > product.qty_available:
                    raise UserError(_('Does not have enough stock of the product %s') % product.name)

                origin = rec.name + '-'
                if rec.travel_id:
                    origin += rec.travel_id.name + '-'
                origin += product.name + ' - ' + str(rec.product_qty)
                # _logger.error(
                #     "origin picking: %s " % origin)

                picking_vals = {
                    'origin': origin,
                    'date': fields.Date.context_today(self),
                    'type': 'out',
                    'state': 'waiting',
                    'move_type': 'direct',
                    'partner_id': users.company_id.partner_id.id,
                    'company_id': users.company_id.id,
                    'stock_move_type_id': move_type_id[0].id,
                    'location_id': location.id,
                    'location_dest_id': location_dest.id,
                    'type_adjustment_id': type_adjustment.id,
                    'picking_type_id': warehouse.out_type_id.id,
                    'authorized': True,
                    'vehicle_id': rec.vehicle_id.id,
                    # 'full_tank': rec.full_tank,
                    'note': rec.notes,
                    'operating_unit_id': warehouse.operating_unit_id.id
                }
                if rec.travel_id:
                    picking_vals['travel_ids'] = [(6, 0, [rec.travel_id.id])]
                    picking_vals['route_id'] = rec.travel_id.route_id.id
                    picking_vals['driver_id'] = rec.travel_id.employee_id.id
                    picking_vals['kilometer'] = rec.travel_id.distance_route

                picking = picking_obj.create(picking_vals)

                # _logger.error(
                #     "product: %s cost %s" % (
                #         product.name,
                #         str(product.standard_price)))

                stock_move_ = {
                    'name': origin,
                    'picking_id': picking.id,
                    'product_id': product.id,
                    'date': fields.Date.context_today(self),
                    'date_expected': fields.Date.context_today(self),
                    'product_uom_qty': rec.product_qty,
                    'product_uom': product.uom_id.id,
                    'product_uos_qty': rec.product_qty,
                    'product_uos': product.uom_id.id,
                    'product_packaging': False,
                    'partner_id': users.company_id.partner_id.id,
                    'location_id': location.id,
                    'location_dest_id': location_dest.id,
                    'tracking_id': False,
                    'company_id': users.company_id.id,
                    'price_unit': product.standard_price,
                    'stock_move_type_id': move_type_id[0].id
                }
                move_obj.create(stock_move_)
                rec.write({'picking_id': picking.id})

                # if rec.picking_id:
                if rec.picking_id.state == 'draft':
                    #_logger.error("picking %s in draft state" % picking.id)
                    rec.picking_id.action_confirm()
                    if rec.picking_id.state != 'assigned':
                        #_logger.error("picking %s in assigned state" % picking.id)
                        rec.picking_id.action_assign()
                        if rec.picking_id.state != 'assigned':
                            raise UserError(_("Could not reserve all requested products. Please use the \'Mark as Todo\' button to handle the reservation manually."))
                if rec.picking_id.state != 'done':
                    #_logger.error("picking %s in not in done state" % picking.id)
                    for move in picking.move_ids_without_package.filtered(lambda m: m.state not in ['done', 'cancel']):
                        for move_line in move.move_line_ids:
                            move_line.qty_done = move_line.product_uom_qty

                    ctx = self._context.copy()
                    ctx.update({
                        'force_vehicle_analytic_id': rec.vehicle_id.account_analytic_id.id})
                    rec.picking_id.with_context(ctx).action_done()

    # @api.multi
    # def generate_qr(self):
    #     report_obj = self.env['report']

    #     str_qr = self.env['ir.config_parameter'].get_param('web.base.url')
    #     str_qr += '/web#id=%s&view_type=form&model=fleet.vehicle.log.fuel&action=\
    #         760&menu_id=1124' % str(self.id)

    #     qr = report_obj.barcode(
    #         barcode_type='QR', value=str_qr, width=500, height=500)
    #     self.image_qr = base64.encodestring(qr)

    #     return {
    #         'type': 'ir.actions.act_url',
    #         'url': self.get_compose_download_url(
    #             self.name + '.png'),
    #         'target': 'new',
    #     }

    # def get_compose_download_url(self, filename, download=True):
    #     base_url = ("/web/content/{model}/{res_id}/image_qr/{filename}"
    #                 "?download={download}")
    #     return base_url.format(
    #         model=self._name, res_id=self.id, filename=filename,
    #         download=json.dumps(download))
