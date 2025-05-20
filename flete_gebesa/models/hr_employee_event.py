# -*- coding: utf-8 -*-
# © <2018> <Aldo Nerio>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class hr_employee_event(models.Model):
    _name = 'hr.employee.event'
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
        string='Positivo',
    )

    amount = fields.Float(
        string='Amount',
    )

    name = fields.Char(
        string='Description', required=True)

    state = fields.Selection(
        [('draft', 'Draft'),
         ('confirm', 'Confirm'),
         ('cancel', 'Cancel')], readonly=True, default='draft')

    date = fields.Date(
        default=fields.Date.context_today,
        required=True,
        string='Fecha',
    )

    notes = fields.Text(
        string='Notas')

    employee_id = fields.Many2one(
        'hr.employee', 'Empleado', index=True, required=True, readonly=False,
        ondelete='restrict')
