# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class FleetVehicleEvent(models.Model):
    _name = 'fleet.vehicle.event'
    _order = "date asc"
    _description = 'descripcion pendiente'

    type = fields.Selection(
        [('driver', 'Driver'),
         ('workshop', 'Workshop'),
         ('customer', 'Customer'),
         ('route', 'Route'),
         ('sales', 'Ventas'),
         ('traffic', 'Trafico'),
         ('lack_operator', 'Falta de Operador')], default='driver',
        string='Tipo'
    )

    positive = fields.Boolean(
        string='Positive',
    )

    amount = fields.Float(
        string='Amount',
    )

    name = fields.Char(
        string='Description', required=True)

    state = fields.Selection(
        [('draft', 'Draft'),
         ('confirm', 'Confirm'),
         ('cancel', ('Cancel'))], readonly=True, default='draft')

    date = fields.Date(
        default=fields.Date.context_today,
        required=True,
    )

    notes = fields.Text(
        string='Notas')

    vehicle_id = fields.Many2one(
        'fleet.vehicle', 'Vehicle', index=True, required=True, readonly=False,
        ondelete='restrict')
