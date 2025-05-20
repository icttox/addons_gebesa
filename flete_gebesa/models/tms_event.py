# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class TmsEvent(models.Model):
    _inherit = 'tms.event'

    type = fields.Selection(
        [('driver', 'Driver'),
         ('workshop', 'Workshop'),
         ('customer', 'Customer'),
         ('route', 'Route'),
         ('sales', 'Ventas'),
         ('traffic', 'Trafico'),
         ('lack_operator', 'Falta de Operador')], default='driver')
    positive = fields.Boolean(
        string='Positive',
    )
    amount = fields.Float(
        string='Amount',
    )
