# -*- coding: utf-8 -*-
# Copyright 2012, Israel Cruz Argil, Argil Consulting
# Copyright 2016, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime

from odoo import api, fields, models, _
from odoo.osv import expression
# from odoo.osv import fields as old_fields


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'
    _description = "Vehicle"
    _order = 'idname asc'
    _rec_name = 'idname'

    """ This ugly code is needed to override fields.function from old api.
    See https://github.com/odoo/odoo/issues/3922
    """

    # _columns = {
    #     'name': old_fields.char('Name', required=True),
    # }
    idname = fields.Char(
        string='Name',
        required=True
    )

    @api.multi
    def name_get(self):
        return [(record.id, record.idname) for record in self]

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        domain = args or []
        cars = self._search(expression.AND([domain, [('idname', operator, name)]]), limit=limit, access_rights_uid=name_get_uid)
        cars += self._search(expression.AND([domain, [('driver_id.name', operator, name)]]), limit=limit, access_rights_uid=name_get_uid)
        rec = self._search([('id', 'in', cars)], limit=limit, access_rights_uid=name_get_uid)
        return self.browse(rec).name_get()


    operating_unit_id = fields.Many2one(
        'operating.unit', string='Operating Unit')
    year_model = fields.Char()
    serial_number = fields.Char()
    registration = fields.Char()
    fleet_type = fields.Selection(
        [('tractor', 'Motorized Unit'),
         ('trailer', 'Trailer'),
         ('dolly', 'Dolly'),
         ('other', 'Other')],
        string='Unit Fleet Type')
    notes = fields.Text()
    active = fields.Boolean(default=True)
    driver_id = fields.Many2one('res.partner', string="Driver")
    employee_id = fields.Many2one(
        'hr.employee',
        string="Driver",
        domain=[('driver', '=', True)])
    expense_ids = fields.One2many('tms.expense', 'unit_id', string='Expenses')
    engine_id = fields.Many2one('fleet.vehicle.engine', string='Engine')
    supplier_unit = fields.Boolean()
    unit_extradata = fields.One2many(
        'tms.extradata', 'vehicle_id',
        string='Extra Data Fields',
        readonly=False)
    insurance_policy = fields.Char()
    insurance_policy_data = fields.Char()
    insurance_expiration = fields.Date()
    insurance_supplier_id = fields.Many2one(
        'res.partner', string='Insurance Supplier')
    insurance_days_to_expire = fields.Integer(
        compute='_compute_insurance_days_to_expire', string='Days to expire')

    @api.depends('model_id.brand_id.name', 'model_id.name', 'license_plate')
    def _compute_vehicle_name(self):
        for record in self:
            record.name = (
                (record.model_id.brand_id.name or _('No Brand')) +
                '/' + (record.model_id.name or _('No Model')) + '/' +
                (record.license_plate or _('No Plate')))

    @api.depends('insurance_expiration')
    def _compute_insurance_days_to_expire(self):
        for rec in self:
            now = datetime.now().date()
            date_expire = (
                rec.insurance_expiration
            ) if rec.insurance_expiration else datetime.now().date()
            delta = date_expire - now
            if delta.days >= -1:
                rec.insurance_days_to_expire = delta.days + 1
            else:
                rec.insurance_days_to_expire = 0
