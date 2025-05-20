# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from __future__ import division
from xml.dom.minidom import parseString
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import requests


class TmsTravel(models.Model):
    _name = 'tms.travel'
    _inherit = ['message.post.show.all', 'tms.travel']

    vel_max_km = fields.Float(
        string='Max Vel - Km/h',
    )

    rp_ms_1700 = fields.Integer(
        string='RP MS > 1700',
    )

    rp_ms_1800 = fields.Integer(
        string='RP MS > 1800',
    )

    rp_ms_1900 = fields.Integer(
        string='RP MS > 1900',
    )

    rp_ms_2000 = fields.Integer(
        string='RP MS > 2000',
    )

    rp_ms_2100 = fields.Integer(
        string='RP MS > 2100',
    )

    rp_ms_max = fields.Float(
        string='RP MS MAX',
    )

    frenados_moderados = fields.Integer(
        string='Moderate Braking',
    )

    frenados_fuertes = fields.Integer(
        string='Strong Braking',
    )

    frenados_max = fields.Integer(
        string='Frenado Max',
    )

    aceleraciones_moderadas = fields.Integer(
        string='Moderate Accelerations',
    )

    aceleraciones_fuertes = fields.Integer(
        string='Strong Accelerations',
    )

    aceleraciones_max = fields.Float(
        string='Aceleraciones Max',
    )

    rendimiento = fields.Float(
        string='Rendimiento',
    )

    employee_two_id = fields.Many2one(
        'hr.employee',
        string='Driver 2',
        domain=[('driver', '=', True)])

    complement = fields.Boolean(
        string='Complemento',
        copy=False,
    )

    refacturacion_id = fields.Many2one(
        'account.invoice',
        string='Factura Cancelada'
    )
    # CARTA PORTE

    partner_id = fields.Many2one(
        'res.partner',
        'Customer', change_default=True)

    partner_order_id = fields.Many2one(
        'res.partner', 'Ordering Contact',
        help="The name and address of the contact who requested the "
        "order or quotation.",)
    # default=(lambda self: self.env['res.partner'].address_get(
    #     self['partner_id'])['contact']))

    partner_invoice_id = fields.Many2one(
        'res.partner', 'Invoice Address',
        help="Invoice address for current Waybill.",)
    # # default=(lambda self: self.env[
    #      'res.partner'].address_get(
    #      self['partner_id'])))

    departure_address_id = fields.Many2one(
        'res.partner', 'Departure Address',
        help="Departure address for current Waybill.", change_default=True)

    arrival_address_id = fields.Many2one(
        'res.partner', 'Arrival Address',
        help="Arrival address for current Waybill.", change_default=True)

    upload_point = fields.Char(change_default=True)

    download_point = fields.Char(change_default=True)

    # LINEAS
    transportable_line_ids = fields.One2many(
        'tms.travel.transportable.line', 'travel_id', string="Transportable")

    waybill_line_ids = fields.One2many(
        'tms.travel.line', 'travel_id', string='Waybill Lines', copy=True)

    tax_line_ids = fields.One2many(
        'tms.travel.taxes', 'travel_id',
        compute='_compute_tax_line_ids',
        string='Tax Lines', store=True)

    amount_freight = fields.Float(
        compute='_compute_amount_freight',
        string='Freight')
    amount_move = fields.Float(
        compute='_compute_amount_move',
        string='Moves')
    amount_highway_tolls = fields.Float(
        compute='_compute_amount_highway_tolls',
        string='Highway Tolls')
    amount_insurance = fields.Float(
        compute='_compute_amount_insurance',
        string='Insurance')
    amount_other = fields.Float(
        compute='_compute_amount_other',
        string='Other')
    amount_untaxed = fields.Float(
        compute='_compute_amount_untaxed',
        string='SubTotal',
        store=True,)
    amount_tax = fields.Float(
        compute='_compute_amount_tax',
        string='Taxes')
    amount_total = fields.Float(
        compute='_compute_amount_total',
        string='Total',
        store=True,
    )

    currency_id = fields.Many2one(
        'res.currency', 'Currency', required=True,
        default=lambda self: self.env.user.company_id.currency_id)

    product_qty = fields.Float(
        compute='_compute_transportable_product',
        string='Sum Qty')
    product_volume = fields.Float(
        compute='_compute_transportable_product',
        string='Sum Volume')
    product_weight = fields.Float(
        compute='_compute_transportable_product',
        string='Sum Weight')

    customer_factor_ids = fields.One2many(
        'tms.factor', 'travel_id',
        string='Waybill Customer Charge Factors',
        domain=[('category', '=', 'customer'), ])

    travel_stop_ids = fields.One2many(
        'tms.travel.stop',
        'travel_id',
        string=('Travel stops'),
    )
    gear_coast_ids = fields.One2many(
        'tms.travel.gear.coast',
        'travel_id',
        string=('Gear coast'),
    )

    shipment_id = fields.Many2one(
        'mrp.shipment',
        string='Shipment',
    )

    tollstation_ids = fields.One2many(
        'tms.travel.tollstation',
        'travel_id',
        string='Tollstations',
    )

    estimated_liters = fields.Float(
        string='Estimated Diesel Liters',
        compute='_compute_estimated_liters',
        store=True,
    )

    estimated_cost = fields.Float(
        string='Estimated Cost',
        compute='_compute_estimated_liters',
        store=True,
    )
    estimated_diesel_user = fields.Float(
        string='Estimated Diesel User',
        compute='_compute_estimated_diesel',
        store=True,
    )
    estimated_cost_user = fields.Float(
        string='Estimated Cost User',
        compute='_compute_estimated_diesel',
        store=True,
    )

    estimated_total_cost = fields.Float(
        string='Estimated total cost',
        compute='_compute_estimated_total_cost',
        store=True,
    )
    estimated_total_cost_without_driver = fields.Float(
        string='Estimated total cost without driver',
        compute='_compute_estimated_total_cost_without_driver',
        store=True,
    )

    final_total_cost_wo_driver = fields.Float(
        string='Costo total al liquidar sin chofer',
        compute='_compute_final_total_cost_without_driver',
        store=False,
    )

    final_total_cost = fields.Float(
        string='Costo total al liquidar',
        readonly=True, related="expense_id.amount_total_total",
        help="Este costo se calcula en la liquidación y se hereda "
        "automáticamente al viaje, considera salario, anticipos (gastos), "
        "casetas, vales de combustible e impuestos."
    )

    refacturacion = fields.Boolean(
        string='Refacturación',
        default=False
    )

    local_travel = fields.Boolean(
        string='Viaje Local',
        default=False
    )

    ingreso_operacion = fields.Float(
        string='Ingreso Operación',
        compute='_compute_ingreso_operacion',
        store=True,
    )

    margen_utilidad = fields.Float(
        string='Margen Utilidad',
        compute='_compute_margen_utilidad',
        store=True,
    )
    margen_utilidad_without_driver = fields.Float(
        string='Margen Utilidad Sin Chofer',
        compute='_compute_margen_utilidad_without_driver',
        store=True,
    )

    margen_final = fields.Float(
        string='Margen Utilidad Final',
        compute='_compute_margen_utilidad_final',
        store=True,
    )

    viaje_pagado = fields.Selection(
        [('paid', 'Viaje Pagado'),
         ('without_paid', 'Viaje Sin Pagar')],
        default='without_paid',
        string='Viaje Pagado',
        readonly=True,
    )

    details_payment = fields.Text(
        string='Datos del Pago',
    )

    pay_day = fields.Datetime(
        string='Fecha Informativa Pago',
        readonly=True,
    )

    attachment_count = fields.Integer(
        string='Attachment Count',
        compute='_compute_count_attachments',
    )
    price_per_km = fields.Float(
        string='Precio por Km',
    )

    gps_url = fields.Text(
        string='URL Gps',
    )

    # purchase_order = fields.Char(
    #     string='Orden de compra',
    # )

    @api.multi
    def print_shipment_data(self):
        self.ensure_one()
        if not self.shipment_id:
            raise UserError(_('This Travel does not have a Shipment'))

        return self.env.ref('paperwork_usa.complement_information_waybill_xlsx')\
            .with_context(discard_logo_check=True).report_action(self.shipment_id)

    @api.one
    def _compute_count_attachments(self):
        for record in self:
            record.attachment_count = self.env['ir.attachment'].search_count([('res_model', '=', 'tms.travel'), ('res_id', '=', record.id)])

    @api.multi
    def paid_travel(self):
        for travel in self:
            if not travel.state == 'progress' and not travel.state == 'draft':
                if not self.env.user.has_group('flete_gebesa.group_decrease_travel_income'):
                    raise ValidationError(_('You do not have privileges to pay for this travel'))
                if not travel.details_payment:
                    raise UserError(_('This action need a Details Payment'))
                travel.viaje_pagado = 'paid'
                travel.pay_day = datetime.today()
            else:
                raise ValidationError(_('The state of the trip cannot be draft or progress'))
        return

    @api.model
    def _compute_transportable_product(self):
        for waybill in self:
            # total_get_amount = 0.0
            for factor in waybill.customer_factor_ids:
                if factor.factor_type in [
                        'distance', 'distance_real', 'percent',
                        'percent_drive', 'travel', 'amount_driver']:
                    for travel in waybill.travel_ids:
                        waybill.distance_route += travel.route_id.distance
                    waybill.distance_real = 0.0
                    # total_get_amount += waybill.customer_factor_ids.get_amount(
                    #     waybill.product_weight, waybill.distance_route,
                    #     waybill.distance_real, waybill.product_qty,
                    #     waybill.product_volume, waybill.amount_total)
                else:
                    for record in waybill.transportable_line_ids:
                        waybill.product_qty = record.quantity
                        if (record.transportable_uom_id.category_id.name ==
                                _('Volume')):
                            waybill.product_volume += record.quantity
                        elif (record.transportable_uom_id.category_id.name ==
                                _('Weight')):
                            waybill.product_weight += record.quantity
                        # total_get_amount += (
                        #     waybill.customer_factor_ids.get_amount(
                        #         waybill.product_weight, waybill.distance_route,
                        #         waybill.distance_real, waybill.product_qty,
                        #         waybill.product_volume, waybill.amount_total))
            # return total_get_amount

    @api.multi
    def _compute_amount_all(self, category):
        for waybill in self:
            field = 0.0
            for line in waybill.waybill_line_ids:
                if (line.product_id.tms_product_category ==
                        category):
                    field += line.price_subtotal
            return field

    @api.depends('amount_untaxed', 'amount_tax')
    def _compute_amount_total(self):
        for waybill in self:
            waybill.amount_total = waybill.amount_untaxed + waybill.amount_tax

    @api.depends('waybill_line_ids')
    def _compute_tax_line_ids(self):
        for waybill in self:
            tax_grouped = {}
            for line in waybill.waybill_line_ids:

                unit_price = (
                    line.unit_price * (1 - (line.discount or 0.0) / 100.0))
                taxes = line.tax_ids.compute_all(
                    unit_price, waybill.currency_id, line.product_qty,
                    line.product_id, waybill.partner_id)
                for tax in taxes['taxes']:
                    val = {
                        'tax_id': tax['id'], 'base': taxes['base'],
                        'tax_amount': tax['amount']}
                    key = waybill.env['account.tax'].browse(tax['id']).id
                    if key not in tax_grouped:
                        tax_grouped[key] = val
                    else:
                        tax_grouped[key]['tax_amount'] += val['tax_amount']
                        tax_grouped[key]['base'] += val['base']
            tax_lines = waybill.tax_line_ids.browse([])
            for tax in tax_grouped.values():
                tax_lines += tax_lines.new(tax)
            waybill.tax_line_ids = tax_lines

    # @api.onchange('customer_factor_ids', 'transportable_line_ids')
    # def _onchange_waybill_line_ids(self):
    #     for rec in self:
    #         for product in rec.waybill_line_ids:
    #             if product.product_id.tms_product_category == 'freight':
    #                 product.write({
    #                     'unit_price': rec._compute_transportable_product()})

    @api.depends('waybill_line_ids')
    def _compute_amount_freight(self):
        for rec in self:
            rec.amount_freight = rec._compute_amount_all('freight')

    @api.depends('waybill_line_ids')
    def _compute_amount_move(self):
        for rec in self:
            rec.amount_move = rec._compute_amount_all('move')

    @api.depends('waybill_line_ids')
    def _compute_amount_highway_tolls(self):
        for rec in self:
            rec.amount_highway_tolls = rec._compute_amount_all('tolls')

    @api.depends('waybill_line_ids')
    def _compute_amount_insurance(self):
        for rec in self:
            rec.amount_insurance = rec._compute_amount_all('insurance')

    @api.depends('waybill_line_ids')
    def _compute_amount_other(self):
        for rec in self:
            rec.amount_other = rec._compute_amount_all('other')

    @api.depends('waybill_line_ids')
    def _compute_amount_untaxed(self):
        for waybill in self:
            for line in waybill.waybill_line_ids:
                waybill.amount_untaxed += line.price_subtotal

    @api.depends('waybill_line_ids')
    def _compute_amount_tax(self):
        for waybill in self:
            for line in waybill.waybill_line_ids:
                waybill.amount_tax += line.tax_amount

### INFORMACION FACTURACION
    invoice_id = fields.Many2one(
        'account.invoice', 'Invoice', readonly=True, copy=False)
    invoice_paid = fields.Boolean(
        compute="_compute_invoice_paid")

    @api.multi
    @api.depends('invoice_id')
    def _compute_invoice_paid(self):
        for rec in self:
            paid = (rec.invoice_id and rec.invoice_id.state == 'paid')
            rec.invoice_paid = paid

    @api.multi
    def action_cancel(self):
        for travel in self:
            if travel.invoice_paid:
                raise ValidationError(
                    _('Could not cancel this waybill because'
                      'the waybill is already paid.'))
            if travel.invoice_id and travel.invoice_id.state != 'cancel':
                raise ValidationError(
                    _('You cannot unlink the invoice of this waybill'
                        ' because the invoice is still valid, '
                        'please check it.'))
            else:
                travel.invoice_id = False
                travel.state = 'cancel'
                travel.message_post(
                    body=_("<h5><strong>Cancelled</strong></h5>"))

            tollstations = travel.tollstation_ids.search([
                ('state', '!=', 'cancel'),
                ('travel_id', '=', travel.id)])
            if len(tollstations) >= 1:
                raise ValidationError(
                    _('If you want to cancel this travel, '
                      'you must cancel the tollstation logs '
                      'attached to this travel'))
            travel.unit_id.write({'status': 'lack_sales'})
            travel.trailer1_id.write({'status': 'lack_sales'})
            travel.trailer2_id.write({'status': 'lack_sales'})
        super().action_cancel()
    #######

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if self.partner_id:
            self.partner_order_id = self.partner_id.address_get(
                ['invoice', 'contact']).get('contact', False)
            self.partner_invoice_id = self.partner_id.address_get(
                ['invoice', 'contact']).get('invoice', False)

    @api.depends('route_id.distance', 'fuel_efficiency_expected')
    def _compute_estimated_liters(self):
        for rec in self:
            if rec.fuel_efficiency_expected != 0:
                rec.estimated_liters = (
                    rec.distance_route) / (rec.fuel_efficiency_expected)
                price = self.env['fuel.history.price'].search([
                    ('fuel_type', '=', 'diesel')], limit=1, order='date desc')
                if price:
                    rec.estimated_cost = (
                        rec.estimated_liters) * (price[0].price)

    @api.depends('route_id.distance', 'rendimiento')
    def _compute_estimated_diesel(self):
        for rec in self:
            if rec.rendimiento > 0:
                rec.estimated_diesel_user = rec.distance_route / rec.rendimiento
                price = self.env['fuel.history.price'].search([
                    ('fuel_type', '=', 'diesel')], limit=1, order='date desc')
                if price:
                    rec.estimated_cost_user = (
                        rec.estimated_diesel_user) * (price[0].price)

    @api.depends('unit_id.performance')
    def _compute_fuel_efficiency_expected(self):
        for rec in self:
            rec.fuel_efficiency_expected = rec.unit_id.performance

    @api.depends('estimated_cost_user', 'tollstation_ids', 'tollstation_ids.state',
                 'advance_ids', 'advance_ids.state', 'driver_factor_ids')
    def _compute_estimated_total_cost(self):
        for rec in self:
            rec.estimated_total_cost = rec.estimated_cost_user
            rec.estimated_total_cost += sum(rec.mapped(
                'tollstation_ids').filtered(
                lambda adv: (adv.state != 'cancel')).mapped('amount'))
            rec.estimated_total_cost += sum(rec.mapped(
                'advance_ids').filtered(
                lambda adv: (adv.state != 'cancel')).mapped('amount'))
            sum_factor = 0
            for factor in rec.driver_factor_ids:
                if factor.factor_type == 'travel':
                    sum_factor += factor.fixed_amount
            rec.estimated_total_cost += sum_factor

    @api.depends('estimated_cost_user', 'tollstation_ids', 'tollstation_ids.state',
                 'advance_ids', 'advance_ids.state')
    def _compute_estimated_total_cost_without_driver(self):
        for rec in self:
            rec.estimated_total_cost_without_driver = rec.estimated_cost_user
            rec.estimated_total_cost_without_driver += sum(rec.mapped(
                'tollstation_ids').filtered(
                lambda adv: (adv.state != 'cancel')).mapped('amount'))
            rec.estimated_total_cost_without_driver += sum(rec.mapped(
                'advance_ids').filtered(
                lambda adv: (adv.state != 'cancel')).mapped('amount'))

    @api.depends('expense_id', 'expense_id.amount_total_total')
    def _compute_final_total_cost_without_driver(self):
        for rec in self:
            rec.final_total_cost_wo_driver = 0.00
            if rec.expense_id:
                rec.final_total_cost_wo_driver =\
                    rec.expense_id.amount_total_total -\
                    rec.expense_id.amount_salary

    @api.one
    def write(self, vals):
        old_total = self.amount_total
        if 'unit_id' in vals.keys():
            unit_id = vals['unit_id']
            vehicle = self.env['fleet.vehicle'].browse(unit_id)
            vehicle.state = 'to_leave'
            travels_ids = self.search([
                ('unit_id', '=', self.unit_id.id),
                ('state', '=', 'draft'),
                ('id', '!=', self.id)])
            if not travels_ids:
                self.unit_id.state = 'lack_sales'
        res = super().write(vals)
        new_total = self.amount_total
        if not self.env.user.has_group('flete_gebesa.group_decrease_travel_income'):
            if new_total < old_total:
                raise UserError(_('No tiene privilegio para disminuir el ingreso del viaje'))
        if not self.waybill_line_ids:
            raise UserError(_('This travel need Waybill Lines'))
        return res

    @api.model
    def create(self, values):
        res = super().create(values)
        if not res.waybill_line_ids:
            raise UserError(_('This travel need Waybill Lines'))
        if not self.env.user.has_group('sales_team.group_sale_manager'):
            raise UserError(_('No tienes suficientes privilegios para realizar esta acccion...'))
        return res

    # @api.depends('waybill_ids', 'waybill_ids.amount_untaxed', 'amount_untaxed')
    @api.depends('amount_untaxed')
    def _compute_ingreso_operacion(self):
        for rec in self:
            # if rec.waybill_ids:
            #     for waybill in rec.waybill_ids:
            #         rec.ingreso_operacion += waybill.amount_untaxed
            # else:
            rec.ingreso_operacion = rec.amount_untaxed

    @api.depends('expense_id', 'ingreso_operacion',
                 'expense_id.amount_total_total', 'expense_id.amount_salary')
    def _compute_margen_utilidad_final(self):
        for rec in self:
            if rec.expense_id and rec.ingreso_operacion:
                rec.margen_final = ((rec.ingreso_operacion - (rec.expense_id.amount_total_total - rec.expense_id.amount_salary)) / rec.ingreso_operacion) * 100
            else:
                rec.margen_final = 0

    @api.depends('ingreso_operacion', 'estimated_total_cost')
    def _compute_margen_utilidad(self):
        for rec in self:
            if rec.estimated_total_cost and rec.ingreso_operacion:
                rec.margen_utilidad = ((rec.ingreso_operacion - rec.estimated_total_cost) / rec.ingreso_operacion) * 100
            else:
                rec.margen_utilidad = 0

    @api.depends('ingreso_operacion', 'estimated_total_cost_without_driver')
    def _compute_margen_utilidad_without_driver(self):
        for rec in self:
            if rec.estimated_total_cost_without_driver and rec.ingreso_operacion:
                rec.margen_utilidad_without_driver = ((rec.ingreso_operacion - rec.estimated_total_cost_without_driver) / rec.ingreso_operacion) * 100
            else:
                rec.margen_utilidad_without_driver = 0

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        for travel in self:
            advances = travel.mapped('advance_ids').filtered(
                lambda adv: adv.state == 'draft')
            advances.write({'employee_id': travel.employee_id.id})
            tollstations = travel.mapped('tollstation_ids').filtered(
                lambda adv: adv.state == 'draft')
            tollstations.write({'employee_id': travel.employee_id.id})
            fuel_logs = travel.mapped('fuel_log_ids').filtered(
                lambda adv: adv.state == 'draft')
            fuel_logs.write({'employee_id': travel.employee_id.id})

    @api.multi
    def get_tollstation_ids(self):
        product = self.env['product.product'].search(
            [('tms_product_category', '=', 'tollstations'),
             ('active', '=', True)], limit=1)
        self.tollstation_ids.unlink()
        axis = 0
        if not product:
            raise ValidationError(
                _('Warning. It was not configured, a product with '
                  'tollstation type'))
        tollstation_obj = self.env['tms.travel.tollstation']
        cost_obj = self.env['tms.route.tollstation.costperaxis']
        axis += self.unit_id.axis
        axis += self.trailer1_id.axis
        axis += self.dolly_id.axis
        axis += self.trailer2_id.axis
        for tollstation in self.route_id.tollstation_ids:
            cost = cost_obj.search([('tollstation_id', '=', tollstation.id),
                                    ('axis', '=', axis)])
            tollstation_obj.create({
                'operating_unit_id': self.operating_unit_id.id,
                'name': tollstation.name,
                'product_id': product.id,
                'state': 'draft',
                'amount': cost.cost_cash if cost else 0.00,
                'travel_id': self.id
            })

    @api.multi
    def action_progress(self):
        res = super().action_progress()
        for travel in self:
            # if not travel.attachment_count or travel.attachment_count == 0:
            #     raise UserError(_('You need to attach a Purchase Order!'))
            if not travel.unit_id:
                raise UserError(_('This travel need a Unit'))
            if not travel.trailer1_id:
                raise UserError(_('This travel need a Trailer'))
            if not travel.employee_id:
                raise UserError(_('This travel need a Employee'))
            if not travel.date_start_real:
                raise UserError(_('This travel need a Date Start Real'))
            travel.unit_id.write({'status': 'active'})
            travel.trailer1_id.write({'status': 'active'})
            travel.trailer2_id.write({'status': 'active'})
        if self.rendimiento <= 0.00:
            raise ValidationError(
                'El campo rendimiento de la pestaña estadisticas no puede '
                'ser igual o menor que cero, es requerido para calcular el'
                ' costo de diesel'
            )
        return res

    @api.multi
    def action_done(self):
        res = super().action_done()
        for travel in self:
            if not travel.date_end_real:
                raise UserError(_('This travel need a Date End Real'))
            travel.unit_id.write({'status': 'lack_sales'})
            travel.trailer1_id.write({'status': 'lack_sales'})
            travel.trailer2_id.write({'status': 'lack_sales'})
        return res

    @api.multi
    def report_ecu(self):
        for travel in self:
            if not travel.date_start_real or not travel.date_end_real:
                raise UserError(_(
                    'This travel need a Date Start Real and Date End Real'))
            # if not vehicle.imei:
            #    raise UserError(_(
            #        'This truck %s has not a valid imei number') % (vehicle.name))
            # fecha_ini = datetime.strptime(
            #     travel.date_start_real, '%Y-%m-%d %H:%M:%S')
            fecha_ini = fields.Datetime.context_timestamp(self, travel.date_start_real)
            fecha_ini = fecha_ini.strftime('%Y-%m-%dT%H:%M:%S')

            # fecha_fin = datetime.strptime(
            #     travel.date_end_real, '%Y-%m-%d %H:%M:%S')
            fecha_fin = fields.Datetime.context_timestamp(self, travel.date_end_real)
            fecha_fin = fecha_fin.strftime('%Y-%m-%dT%H:%M:%S')
            url = travel.operating_unit_id.company_id.urlecho
            if not url:
                raise UserError(_(
                    'URL incorecta'))
            usuariogps = travel.operating_unit_id.company_id.usuariogps
            if not usuariogps:
                raise UserError(_(
                    'Usuario incorrecto'))
            passwordgps = travel.operating_unit_id.company_id.passwordgps
            if not passwordgps:
                raise UserError(_(
                    'Password incorrecto'))
            db = url
            xml = """<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:tem="http://tempuri.org/">
                <soap:Header xmlns:wsa="http://www.w3.org/2005/08/addressing">
                 <wsa:Action>http://tempuri.org/IGpsWebServices/GetReportEcuByDateTime</wsa:Action>
                 <wsa:To>https://67.219.149.214:9003/ws</wsa:To>
               </soap:Header>
               <soap:Body>
                  <tem:GetReportEcuByDateTime>
                     <tem:userName>%s</tem:userName>
                     <tem:userPassword>%s</tem:userPassword>
                     <tem:from>%s</tem:from>
                     <tem:to>%s</tem:to>
                  </tem:GetReportEcuByDateTime>
               </soap:Body>
            </soap:Envelope>""" % (usuariogps, passwordgps, fecha_ini, fecha_fin)
            headers = {
                'Content-Type': 'application/soap+xml; charset=utf-8',
            }
            try:
                req = requests.request(
                    'POST', db, data=xml,
                    headers=headers, verify=False)
            except requests.HTTPError as error:
                raise UserError(_(
                    'Error al conectarse con GPS'
                    'Error: %s.') % (error))

            try:
                resultados_mensaje = req.content
                dom = parseString(resultados_mensaje)

                status = dom.getElementsByTagName('b:status')[0].firstChild.nodeValue
            except:
                raise UserError(_(
                    'Ocurrio un error del lado del proveedor del GPS \n'
                    'Error: \n %s.') % (resultados_mensaje))
            if status == 'Ok':

                rows = dom.getElementsByTagName(
                    'b:ReportEcuByDateTimeRow')

                # trucks_wimei = self.env['fleet.vehicle'].search([('imei', '!=', False)])

                for row in rows:
                    row_imei = row.getElementsByTagName('b:UnitImei')[0].firstChild.nodeValue
                    # row_imei2 = row.getElementsByTagName('b:UnitName')[0].firstChild.nodeValue
                    if travel.unit_id.imei == row_imei:
                        row_maxSpeed = row.getElementsByTagName('b:maxSpeed')[0].firstChild
                        if row_maxSpeed:
                            travel.vel_max_km = row_maxSpeed.nodeValue
                        row_rpms_max = row.getElementsByTagName('b:rpmMax')[0].firstChild
                        if row_rpms_max:
                            travel.rp_ms_max = row_rpms_max.nodeValue
                        row_than_1700 = row.getElementsByTagName('b:rpmGreaterThan1700')[0].firstChild
                        if row_than_1700:
                            travel.rp_ms_1700 = row_than_1700.nodeValue
                        row_than_1800 = row.getElementsByTagName('b:rpmGreaterThan1800')[0].firstChild
                        if row_than_1800:
                            travel.rp_ms_1800 = row_than_1800.nodeValue
                        row_than_1900 = row.getElementsByTagName('b:rpmGreaterThan1900')[0].firstChild
                        if row_than_1900:
                            travel.rp_ms_1900 = row_than_1900.nodeValue
                        row_than_2000 = row.getElementsByTagName('b:rpmGreaterThan2000')[0].firstChild
                        if row_than_2000:
                            travel.rp_ms_2000 = row_than_2000.nodeValue
                        row_than_2100 = row.getElementsByTagName('b:rpmGreaterThan2100')[0].firstChild
                        if row_than_2100:
                            travel.rp_ms_2100 = row_than_2100.nodeValue

                        row_breakModerate = row.getElementsByTagName('b:breakModerate')[0].firstChild
                        if row_breakModerate:
                            travel.frenados_moderados = row_breakModerate.nodeValue
                        row_breakHard = row.getElementsByTagName('b:breakHard')[0].firstChild
                        if row_breakHard:
                            travel.frenados_fuertes = row_breakHard.nodeValue
                        row_breakMax = row.getElementsByTagName('b:breakMax')[0].firstChild
                        if row_breakMax:
                            travel.frenados_max = row_breakMax.nodeValue

                        row_accelerationModerate = row.getElementsByTagName('b:accelerationModerate')[0].firstChild
                        if row_accelerationModerate:
                            travel.aceleraciones_moderadas = row_accelerationModerate.nodeValue
                        row_accelerationHard = row.getElementsByTagName('b:accelerationHard')[0].firstChild
                        if row_accelerationHard:
                            travel.aceleraciones_fuertes = row_accelerationHard.nodeValue
                        row_accelerationMax = row.getElementsByTagName('b:accelerationMax')[0].firstChild
                        if row_accelerationMax:
                            travel.aceleraciones_max = row_accelerationMax.nodeValue

            else:
                message_body = u"<b>%s:</b> %s" % (
                    (u"El servicio de ECU regresó el siguiente error: "), status)
                travel.message_post(body=message_body)

                # for truck in trucks_wimei:
                #    if truck.imei == row_imei:
                #        truck.latitude = lat
                #        truck.longitude = lon
                # if row_imei != self.imei:
                #     continue
        return True

    @api.multi
    def report_stop(self):
        stop_obj = self.env['tms.travel.stop']
        for travel in self:
            if not travel.date_start_real or not travel.date_end_real:
                raise UserError(_(
                    'This travel need a Date Start Real and Date End Real'))
            # fecha_ini = datetime.strptime(
            #     travel.date_start_real, '%Y-%m-%d %H:%M:%S')
            fecha_ini = fields.Datetime.context_timestamp(self, travel.date_start_real)
            fecha_ini = fecha_ini.strftime('%Y-%m-%dT%H:%M:%S')

            # fecha_fin = datetime.strptime(
            #     travel.date_end_real, '%Y-%m-%d %H:%M:%S')
            fecha_fin = fields.Datetime.context_timestamp(self, travel.date_end_real)
            fecha_fin = fecha_fin.strftime('%Y-%m-%dT%H:%M:%S')

            url = 'https://www.logisticgps.com/WebService.php'
            if not url:
                raise UserError(_(
                    'URL incorecta'))
            usuariogps = travel.operating_unit_id.company_id.usuariogps
            if not usuariogps:
                raise UserError(_(
                    'Usuario incorrecto'))
            passwordgps = travel.operating_unit_id.company_id.passwordgps
            if not passwordgps:
                raise UserError(_(
                    'Password incorrecto'))

            imei = travel.unit_id.imei
            if not imei:
                raise UserError(_(
                    'IMEI incorrecto'))

            xml = """
                <soapenv:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:web="https://www.logisticgps.com/WebService.php">
                    <soapenv:Header/>
                    <soapenv:Body>
                        <web:GetStopReport soapenv:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
                            <userName xsi:type="xsd:string">%s</userName>
                            <password xsi:type="xsd:string">%s</password>
                            <unit xsi:type="xsd:string">%s</unit>
                            <fromDate xsi:type="xsd:dateTime">%s</fromDate>
                            <toDate xsi:type="xsd:dateTime">%s</toDate>
                            <duration xsi:type="xsd:int"></duration>
                        </web:GetStopReport>
                    </soapenv:Body>
                </soapenv:Envelope>
                """ % (usuariogps, passwordgps, imei, fecha_ini, fecha_fin)
            headers = {
                'Content-Type': 'application/soap+xml; charset=utf-8',
            }

            try:
                req = requests.request(
                    'POST', url, data=xml,
                    headers=headers, verify=False)
            except requests.HTTPError as error:
                raise UserError(_(
                    'Error al conectarse con GPS'
                    'Error: %s.') % (error))

            try:
                resultados_mensaje = req.content
                dom = parseString(resultados_mensaje)

                status = dom.getElementsByTagName('status')[0].firstChild.nodeValue
            except:
                raise UserError(_(
                    'Ocurrio un error del lado del proveedor del GPS \n'
                    'Error: \n %s.') % (resultados_mensaje))
            if status == '0':
                rows = dom.getElementsByTagName(
                    'item')
                travel.travel_stop_ids.unlink()
                for row in rows:
                    adress = row.getElementsByTagName('address')[0].firstChild
                    if adress:
                        adress = adress.nodeValue
                    else:
                        adress = 'N/A'
                    stop_obj.create({
                        'travel_id': travel.id,
                        'address': adress,
                        'distance': float(row.getElementsByTagName(
                            'distance')[0].firstChild.nodeValue.replace(',', '')) or 0.00,
                        'latitude': float(row.getElementsByTagName(
                            'latitude')[0].firstChild.nodeValue.replace(',', '')) or 0.00,
                        'longitude': float(row.getElementsByTagName(
                            'longitude')[0].firstChild.nodeValue.replace(',', '')) or 0.00,
                        'duration': row.getElementsByTagName(
                            'duration')[0].firstChild.nodeValue or False,
                        'unit_name': row.getElementsByTagName(
                            'unitName')[0].firstChild.nodeValue or False,
                        'from_date': row.getElementsByTagName(
                            'fromDateTime')[0].firstChild.nodeValue or False,
                        'to_date': row.getElementsByTagName(
                            'toDateTime')[0].firstChild.nodeValue or False
                    })
        return True

    @api.multi
    def get_no_gear_coast_report(self):
        gear_coast_obj = self.env['tms.travel.gear.coast']
        for travel in self:
            if not travel.date_start_real or not travel.date_end_real:
                raise UserError(_(
                    'This travel need a Date Start Real and Date End Real'))
            # fecha_ini = datetime.strptime(
            #     travel.date_start_real, '%Y-%m-%d %H:%M:%S')
            fecha_ini = fields.Datetime.context_timestamp(self, travel.date_start_real)
            fecha_ini = fecha_ini.strftime('%Y-%m-%dT%H:%M:%S')

            # fecha_fin = datetime.strptime(
            #     travel.date_end_real, '%Y-%m-%d %H:%M:%S')
            fecha_fin = fields.Datetime.context_timestamp(self, travel.date_end_real)
            fecha_fin = fecha_fin.strftime('%Y-%m-%dT%H:%M:%S')

            url = 'https://www.logisticgps.com/WebService.php'
            if not url:
                raise UserError(_(
                    'URL incorecta'))
            usuariogps = travel.operating_unit_id.company_id.usuariogps
            if not usuariogps:
                raise UserError(_(
                    'Usuario incorrecto'))
            passwordgps = travel.operating_unit_id.company_id.passwordgps
            if not passwordgps:
                raise UserError(_(
                    'Password incorrecto'))

            imei = travel.unit_id.imei
            if not imei:
                raise UserError(_(
                    'IMEI incorrecto'))

            xml = """
                <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:web="https://www.logisticgps.com/WebService.php">
                    <soapenv:Header/>
                    <soapenv:Body>
                        <web:GetNoGearCoastReport>
                            <userName>%s</userName>
                            <password>%s</password>
                            <units>
                                <item>%s</item>
                            </units>
                            <fromDate>%s</fromDate>
                            <toDate>%s</toDate>
                        </web:GetNoGearCoastReport>
                    </soapenv:Body>
                </soapenv:Envelope>
                """ % (usuariogps, passwordgps, imei, fecha_ini, fecha_fin)
            headers = {
                'Content-Type': 'application/soap+xml; charset=utf-8',
            }
            try:
                req = requests.request(
                    'POST', url, data=xml,
                    headers=headers, verify=False)
            except requests.HTTPError as error:
                raise UserError(_(
                    'Error al conectarse con GPS'
                    'Error: %s.') % (error))

            try:
                resultados_mensaje = req.content
                dom = parseString(resultados_mensaje)

                status = dom.getElementsByTagName('status')[0].firstChild.nodeValue
            except:
                raise UserError(_(
                    'Ocurrio un error del lado del proveedor del GPS \n'
                    'Error: \n %s.') % (resultados_mensaje))
            if status == '0':
                rows = dom.getElementsByTagName(
                    'item')
                travel.gear_coast_ids.unlink()
                for row in rows:
                    gear_coast_obj.create({
                        'travel_id': travel.id,
                        'begin_date_time': row.getElementsByTagName(
                            'beginDateTime')[0].firstChild.nodeValue or False,
                        'begin_speed': float(row.getElementsByTagName(
                            'beginSpeed')[0].firstChild.nodeValue) or 0.00,
                        'begin_latitude': float(row.getElementsByTagName(
                            'beginLatitude')[0].firstChild.nodeValue) or 0.00,
                        'begin_longitude': float(row.getElementsByTagName(
                            'beginLongitude')[0].firstChild.nodeValue) or 0.00,
                        'end_date_time': row.getElementsByTagName(
                            'endDateTime')[0].firstChild.nodeValue or False,
                        'end_speed': float(row.getElementsByTagName(
                            'endSpeed')[0].firstChild.nodeValue) or 0.00,
                        'end_latitude': float(row.getElementsByTagName(
                            'endLatitude')[0].firstChild.nodeValue) or 0.00,
                        'end_longitude': float(row.getElementsByTagName(
                            'endLongitude')[0].firstChild.nodeValue) or 0.00,
                        'distance': float(row.getElementsByTagName(
                            'distance')[0].firstChild.nodeValue) or 0.00,
                        'duration': row.getElementsByTagName(
                            'duration')[0].firstChild.nodeValue or False,
                        'max_speed': float(row.getElementsByTagName(
                            'maxSpeed')[0].firstChild.nodeValue) or 0.00,
                        'avg_speed': float(row.getElementsByTagName(
                            'avgSpeed')[0].firstChild.nodeValue) or 0.00
                    })
        return True

    @api.multi
    def print_cartas_porte(self):
        ctx = self.env.context.copy()
        ctx.update({'default_product_id': self.id})
        return {
            'name': _('Monto Real'),
            'type': 'ir.actions.act_window',
            'res_model': 'tms.wizard.real.amount',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': ctx,
        }
