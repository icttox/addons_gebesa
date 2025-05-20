# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, UserError


class TmsExpense(models.Model):
    _name = 'tms.expense'
    _inherit = ['message.post.show.all', 'tms.expense']

    tollstation_ids = fields.One2many(
        'tms.travel.tollstation',
        'expense_id',
        string='Advances',
        readonly=True
    )
    amount_tollstation = fields.Float(
        compute='_compute_amount_tollstation',
        string='Tollstations',
        store=True
    )

    evidence = fields.Boolean(
        string=_('Evidences'),
        default=False,
        store=True,
    )
    estimated_liters = fields.Float(
        string=_('Liters Estimated Route'),
        compute='_compute_estimated_liters',
        store=True,
        readonly=True,
    )
    estimated_liters_scanner = fields.Float(
        string=_('Liters Estimated Scanner'),
        compute='_compute_estimated_liters_scanner',
        store=True,
        readonly=True,
    )
    liters_scanner = fields.Float(
        string=_('Liters Scanner'),
    )
    amount_estimated_liters_scanner = fields.Float(
        string=_('Amount Liters Estimated Scanner'),
        compute='_compute_estimated_liters_scanner',
        store=True,
        readonly=True,
    )
    diff_liters = fields.Float(
        string=_('Difference (Voucher - Estimated Scanner)'),
        compute='_compute_diff_liters',
        store=True,
        readonly=True,
    )
    amount_diff_liters = fields.Float(
        string=_('Amount Difference (Voucher - Estimated Scanner)'),
        compute='_compute_diff_liters',
        store=True,
        readonly=True,
    )
    estimated_liters_gps = fields.Float(
        string=_('Liters Estimated GPS'),
        compute='_compute_estimated_liters_gps',
        store=True,
        readonly=True,
    )
    amount_estimated_liters_gps = fields.Float(
        string=_('Amount Liters Estimated GPS'),
        compute='_compute_estimated_liters_gps',
        store=True,
        readonly=True,
    )
    diff_liters_gps = fields.Float(
        string=_('Difference (Voucher - Estimated GPS)'),
        compute='_compute_estimated_liters_gps',
        store=True,
        readonly=True,
    )
    amount_diff_liters_gps = fields.Float(
        string=_('Amount Difference (Voucher - Estimated GPS)'),
        compute='_compute_estimated_liters_gps',
        store=True,
        readonly=True,
    )
    calculated_salary = fields.Float(
        string='Calculated Salary',
        compute='_compute_calculated_salary',
    )

    fuel_efficiency_real = fields.Float(
        compute='_compute_fuel_efficiency_real',
        store=True,
    )

    cancellation_note = fields.Text(
        string='Motivo de Cancelacion',
        copy=False,
    )

    partner_ids = fields.Many2many(
        'res.partner',
        compute='_compute_customer_ids',
        string='Cliente'
    )

    @api.multi
    def action_confirm(self):
        kms_obj = self.env['tms.hist.kms.traveled']

        for expense in self:
            if expense.move_id:
                continue
            for travels in expense.travel_ids:
                for tires in travels.unit_id.tires_id:
                    tires.kms_traveled = tires.kms_traveled + expense.distance_loaded_real
                    unit_id_vals = {
                        'tire_id': tires.id,
                        'tms_expense_id': expense.id,
                        'kms_traveled': expense.distance_loaded_real,
                        'date': fields.Datetime.now(),
                    }
                    kms_obj.create(unit_id_vals)

                for tires in travels.trailer1_id.tires_id:
                    tires.kms_traveled = tires.kms_traveled + expense.distance_loaded_real
                    trailer1_id_vals = {
                        'tire_id': tires.id,
                        'tms_expense_id': expense.id,
                        'kms_traveled': expense.distance_loaded_real,
                        'date': fields.Datetime.now(),
                    }
                    kms_obj.create(trailer1_id_vals)

                for tires in travels.dolly_id.tires_id:
                    tires.kms_traveled = tires.kms_traveled + expense.distance_loaded_real
                    dolly_vals = {
                        'tire_id': tires.id,
                        'tms_expense_id': expense.id,
                        'kms_traveled': expense.distance_loaded_real,
                        'date': fields.Datetime.now(),
                    }
                    kms_obj.create(dolly_vals)

                for tires in travels.trailer2_id.tires_id:
                    tires.kms_traveled = tires.kms_traveled + expense.distance_loaded_real
                    trailer2_id_vals = {
                        'tire_id': tires.id,
                        'tms_expense_id': expense.id,
                        'kms_traveled': expense.distance_loaded_real,
                        'date': fields.Datetime.now(),
                    }
                    kms_obj.create(trailer2_id_vals)

        res = super().action_confirm()

    # @api.depends('travel_ids', 'travel_ids.waybill_ids', 'travel_ids.waybill_ids.partner_id')
    @api.depends('travel_ids', 'travel_ids.partner_id')
    def _compute_customer_ids(self):
        for rec in self:
            partner_ids = []
            for travel in rec.travel_ids:
                # for waybill in travel.waybill_ids:
                #     partner_ids.append(waybill.partner_id.id)
                partner_ids.append(travel.partner_id.id)
            rec.partner_ids = partner_ids

    @api.model
    def create(self, vals):
        if vals['distance_loaded_real'] <= 0.00:
            raise ValidationError(_('Kilometros Scanner must be greator than zero'))
        if vals['liters_scanner'] <= 0.00:
            raise ValidationError(_('Liters Scanner must be greator than zero'))
        if vals['distance_real'] <= 0.00:
            raise ValidationError(_('Kilometros GPS must be greator than zero'))

        return super().create(vals)

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        for rec in self:
            if rec.distance_loaded_real <= 0.00:
                raise ValidationError(_('Kilometros Scanner must be greator than zero'))
            if rec.liters_scanner <= 0.00:
                raise ValidationError(_('Liters Scanner must be greator than zero'))
            if rec.distance_real <= 0.00:
                raise ValidationError(_('Kilometros GPS must be greator than zero'))
            #print rec
        return res

    @api.multi
    def action_cancel(self):
        kms_obj = self.env['tms.hist.kms.traveled']

        for rec in self:
            if not rec.cancellation_note:
                raise UserError(_('Debes capturar el motivo de cancelacion de esta Liquidacion'))
            if not self.env.user.has_group('flete_gebesa.group_cancel_waybill_gebesa'):
                raise UserError(_('Solo Gerencia puede cancelar esta Liquidacion'))

            for travels in rec.travel_ids:
                for tires in travels.unit_id.tires_id:
                    tires.kms_traveled = tires.kms_traveled - rec.distance_loaded_real
                    expense_line = self.env['tms.hist.kms.traveled'].search([('tms_expense_id', '=', rec.id)])
                    expense_line.unlink()

                for tires in travels.trailer1_id.tires_id:
                    tires.kms_traveled = tires.kms_traveled - rec.distance_loaded_real
                    expense_line = self.env['tms.hist.kms.traveled'].search([('tms_expense_id', '=', rec.id)])
                    expense_line.unlink()

                for tires in travels.dolly_id.tires_id:
                    tires.kms_traveled = tires.kms_traveled - rec.distance_loaded_real
                    expense_line = self.env['tms.hist.kms.traveled'].search([('tms_expense_id', '=', rec.id)])
                    expense_line.unlink()

                for tires in travels.trailer2_id.tires_id:
                    tires.kms_traveled = tires.kms_traveled - rec.distance_loaded_real
                    expense_line = self.env['tms.hist.kms.traveled'].search([('tms_expense_id', '=', rec.id)])
                    expense_line.unlink()

            return super().action_cancel()

    @api.multi
    def action_draft(self):
        for rec in self:
            if not self.env.user.has_group('flete_gebesa.group_cancel_waybill_gebesa'):
                raise UserError(_('Solo Gerencia puede revertir a borrador este registro.'))
            return super().action_draft()

    @api.depends('distance_loaded_real', 'fuel_qty')
    def _compute_fuel_efficiency_real(self):
        for rec in self:
            try:
                rec.fuel_efficiency_real = (
                    rec.distance_loaded_real / rec.fuel_qty)
            except ZeroDivisionError:
                rec.fuel_efficiency_real = 0.0

    @api.depends('amount_balance', 'amount_diff_liters')
    def _compute_calculated_salary(self):
        for rec in self:
            rec.calculated_salary = (rec.amount_balance -
                                     rec.amount_diff_liters)

    @api.depends('travel_ids', 'expense_line_ids')
    def _compute_amount_tollstation(self):
        for rec in self:
            rec.amount_tollstation = 0
            for travel in rec.travel_ids:
                for tollstation in travel.tollstation_ids:
                    rec.amount_tollstation += tollstation.amount

    @api.depends('travel_ids', 'expense_line_ids', 'amount_tollstation')
    def _compute_amount_subtotal_total(self):
        for rec in self:
            rec.amount_subtotal_total = 0
            for travel in rec.travel_ids:
                for fuel_log in travel.fuel_log_ids:
                    rec.amount_subtotal_total += (
                        fuel_log.price_subtotal +
                        fuel_log.special_tax_amount)
            for line in rec.expense_line_ids:
                if line.line_type == 'real_expense':
                    rec.amount_subtotal_total += line.price_subtotal
            rec.amount_subtotal_total += rec.amount_balance
            rec.amount_subtotal_total += rec.amount_tollstation

    @api.depends('travel_ids', 'fuel_qty')
    def _compute_estimated_liters(self):
        for rec in self:
            rec.estimated_liters = 0.00
            for travel in rec.travel_ids:
                rec.estimated_liters += travel.estimated_liters

    @api.depends('fuel_qty', 'liters_scanner')
    def _compute_diff_liters(self):
        for rec in self:
            rec.diff_liters = rec.fuel_qty - rec.liters_scanner
            price = self.env['fuel.history.price'].search([
                ('fuel_type', '=', 'diesel')], limit=1, order='date desc')
            if price:
                rec.amount_diff_liters = rec.diff_liters * price.price

    @api.depends('distance_loaded_real', 'fuel_efficiency_real')
    def _compute_estimated_liters_scanner(self):
        for rec in self:
            rec.estimated_liters_scanner = 0.00
            if rec.fuel_efficiency_real != 0:
                rec.estimated_liters_scanner = (
                    rec.distance_loaded_real / rec.fuel_efficiency_real)
            price = self.env['fuel.history.price'].search([
                ('fuel_type', '=', 'diesel')], limit=1, order='date desc')
            if price:
                rec.amount_estimated_liters_scanner = (
                    rec.estimated_liters_scanner * price.price)

    @api.depends('distance_real', 'fuel_efficiency_real')
    def _compute_estimated_liters_gps(self):
        for rec in self:
            rec.estimated_liters_gps = 0.00
            if rec.fuel_efficiency_real != 0:
                rec.estimated_liters_gps = (
                    rec.distance_real / rec.fuel_efficiency_real)
            rec.diff_liters_gps = rec.fuel_qty - rec.estimated_liters_gps
            price = self.env['fuel.history.price'].search([
                ('fuel_type', '=', 'diesel')], limit=1, order='date desc')
            if price:
                rec.amount_estimated_liters_gps = (
                    rec.estimated_liters_gps * price.price)
                rec.amount_diff_liters_gps = rec.diff_liters_gps * price.price

    @api.multi
    def get_travel_info(self):
        super().get_travel_info()
        for rec in self:
            for travel in rec.travel_ids:
                for tollstation in travel.tollstation_ids:
                    # Creating tollstation lines
                    rec.create_tollstation_line(tollstation, travel)
                    # Finish creating tollstation lines
                # travel.report_ecu()
                # time.sleep(60)
                # travel.report_stop()
                # time.sleep(60)
                # travel.get_no_gear_coast_report()

    @api.model
    def prepare_move_line(self, name, ref, account_id,
                          debit, credit, journal_id,
                          partner_id, operating_unit_id):
        res = super().prepare_move_line(
            name, ref, account_id, debit, credit, journal_id,
            partner_id, operating_unit_id)
        res[2]['analytic_account_id'] = self.unit_id.account_analytic_id.id
        return res

    @api.multi
    def create_tollstation_line(self, tollstation, travel):
        if tollstation.state not in ('confirmed', 'cancel'):
            raise ValidationError(_(
                'Oops! All the tollstation must be confirmed'
                ' or cancelled \n '
                'Name of tollstation not confirmed or cancelled: ' +
                tollstation.name +
                '\n State: ' + tollstation.state))
        if tollstation.state != 'cancel':
            tollstation.write({
                'state': 'closed',
                'expense_id': self.id
            })

    @api.multi
    def unattach_info(self):
        for rec in self:
            tollstation = self.env['tms.travel.tollstation'].search(
                [('expense_id', '=', rec.id)])
            tollstation.write({
                'expense_id': False,
                'state': 'confirmed'
            })
        return super().unattach_info()

    @api.multi
    def unlink(self):
        for rec in self:
            tollstation = self.env['tms.travel.tollstation'].search(
                [('expense_id', '=', rec.id)])
            tollstation.write({
                'expense_id': False,
                'state': 'confirmed'
            })
        return super().unlink()

    @api.depends('travel_ids')
    def get_driver_salary(self, travel):
        for rec in self:
            driver_salary = 0.0
            income = 0.0
            for line in travel.waybill_line_ids:
                if line.product_id.apply_for_salary:
                    income += line.price_subtotal
            # if travel.currency_id.name == 'USD':
            #     income = (income *
            #               self.env.user.company_id.expense_currency_rate)
            if travel.driver_factor_ids:
                for factor in travel.driver_factor_ids:
                    driver_salary += factor.get_amount(
                        weight=travel.product_weight,
                        distance=travel.distance_route,
                        distance_real=rec.distance_real,
                        qty=travel.product_qty,
                        volume=travel.product_volume,
                        income=income,
                        employee=rec.employee_id)
            else:
                raise ValidationError(_(
                    'Oops! You have not defined a Driver factor in '
                    'the Travel or the Waybill\nTravel: %s' %
                    travel.name))
            return driver_salary
