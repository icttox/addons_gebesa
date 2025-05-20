# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class Tires(models.Model):
    _name = 'tires'
    _rec_name = 'code_tires'
    _inherit = ['message.post.show.all', 'mail.thread']

    code_tires = fields.Char(
        string=_('Code'),
    )

    new_tires = fields.Selection(
        [('new', 'New'),
         ('used', 'Used'),
         ('repaired', 'Repaired')],
        string='New / Used',
    )

    price_tires = fields.Float(
        string='Price'
    )

    commitment_date = fields.Date(
        string='Commitment Date',
    )

    partner_tires_id = fields.Many2one(
        'res.partner',
        string='Partner'
    )

    mark = fields.Many2one(
        'fleet.vehicle.model.brand',
        string='Mark',
    )

    series_tires = fields.Char(
        string='Series'
    )

    measure = fields.Char(
        string='Measure'
    )

    radi = fields.Selection(
        [('all_position', 'All Position'),
         ('traction', 'Traction'),
         ('drag', 'Drag'),
         ('direction', 'Direction')],
        string='Type',
    )

    floor = fields.Float(
        string='Remaining floor mm'
    )

    low_date = fields.Date(
        string='Low Date'
    )

    comments_tires = fields.Text(
        string='Comments',
    )

    fleet_vehicle_id = fields.Many2one(
        'fleet.vehicle',
        string='Vehicle'
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )
    sequence = fields.Integer(default=1)

    tms_tire_hist_ids = fields.One2many(
        'tms.tire.position.hist',
        'tire_id',
        string='Tires',
    )

    tms_kms_traveled_ids = fields.One2many(
        'tms.hist.kms.traveled',
        'tire_id',
        string='KMS Traveled',
    )

    position = fields.Selection(
        [('1', '1'),
            ('2', '2'),
            ('3', '3'),
            ('4', '4'),
            ('5', '5'),
            ('6', '6'),
            ('7', '7'),
            ('8', '8'),
            ('9', '9'),
            ('10', '10'),
            ('11', '11'),
            ('12', '12'),
            ('99', 'Spare')],
        string='Position'
    )

    reason_for_cancellation = fields.Text(
        string='Reason for Cancellation',
    )

    kms_traveled = fields.Float(
        string='KMS Traveled',
    )

    reading_date = fields.Datetime(
        string='Reading Date',
    )

    num_invoice = fields.Char(
        string='Number Invoice',
    )

    mm_original = fields.Float(
        string='MM Original',
    )

    original_cost = fields.Float(
        string='Original Cost',
    )

    cost_x_km = fields.Float(
        string='Cost x KM',
        compute='compute_cost_x_km',
        store=True,
    )

    km_mm = fields.Float(
        string='KM / MM original',
        compute='compute_km_mm',
        store=True,
    )

    @api.depends('kms_traveled', 'original_cost')
    def compute_cost_x_km(self):
        for tire in self:
            if tire.kms_traveled > 0:
                tire.cost_x_km = tire.original_cost / tire.kms_traveled
            else:
                tire.cost_x_km = 0

    @api.depends('kms_traveled', 'mm_original')
    def compute_km_mm(self):
        for tire in self:
            if tire.mm_original > 0:
                tire.km_mm = tire.kms_traveled / tire.mm_original
            else:
                tire.km_mm = 0

    _sql_constraints = [
        ('values_tires_uniq', "unique(fleet_vehicle_id,position)",
         _('The unit already contains a tire in that position')),
    ]

    @api.multi
    def toggle_active(self):
        res = super().toggle_active()

        for tires in self:
            if tires.active is False and not tires.reason_for_cancellation:
                raise UserError(_('Enter the reason for cancellation'))

        return res

    @api.model
    def create(self, vals):
        res = super().create(vals)
        hist_obj = self.env['tms.tire.position.hist']

        his_vals = {
            'tire_id': res.id,
            'unit_new_id': res.fleet_vehicle_id.id,
            'unit_old_id': res.fleet_vehicle_id.id,
            'odometer_new': res.fleet_vehicle_id.odometer,
            'odometer_old': res.fleet_vehicle_id.odometer,
            'position_new': vals['position'],
            'position_old': vals['position'],
            'date': fields.Datetime.now(),
        }
        hist_obj.create(his_vals)

        return res

    @api.constrains('fleet_vehicle_id', 'position')
    def check_position(self):
        for tire in self:
            tipo = tire.fleet_vehicle_id.fleet_type
            if tipo:
                if tipo in ['tractor'] and tire.position in ['11', '12']:
                    raise UserError('La posición de la llanta no puede ser mayor a 10')
                if tipo not in ['tractor', 'trailer'] and tire.position in ['9', '10', '11', '12']:
                    raise UserError('La posición de la llanta no puede ser mayor a 8')
            else:
                if tire.position:
                    raise UserError('La llanta no está asignada a un vehículo, no puede tener posición')

    @api.multi
    def write(self, vals):

        hist_obj = self.env['tms.tire.position.hist']
        vehicle = 'fleet_vehicle_id'
        position = 'position'
        if vehicle in vals.keys() or position in vals.keys():
            odometer_new = ''
            odometer_old = self.fleet_vehicle_id.odometer
            vehicle_old = self.fleet_vehicle_id.id
            vehicle_new = ''
            if vehicle in vals:
                vehicle_new = vals['fleet_vehicle_id']
                odometer_new = self.env['fleet.vehicle'].browse(vehicle_new).odometer
            else:
                vehicle_new = self.fleet_vehicle_id.id
                odometer_new = self.fleet_vehicle_id.odometer

            position_new = ''
            position_old = self.position
            if position in vals:
                position_new = vals['position']
            else:
                position_new = self.position

            his_vals = {
                'tire_id': self.id,
                'unit_old_id': vehicle_old,
                'unit_new_id': vehicle_new,
                'position_old': position_old,
                'position_new': position_new,
                'odometer_old': odometer_old,
                'odometer_new': odometer_new,
                'date': fields.Datetime.now(),
            }
            hist_obj.create(his_vals)

        return super().write(vals)
