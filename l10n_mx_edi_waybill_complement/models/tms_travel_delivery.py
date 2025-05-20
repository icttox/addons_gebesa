# -*- coding: utf-8 -*-

from odoo import models, fields


class TmsTravelDelivery(models.Model):
    _name = 'tms.travel.delivery'
    _rec_name = 'partner_id'
    _order = 'sequence'
    _description = 'descripcion pendiente'

    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
    )
    travel_id = fields.Many2one(
        'tms.travel',
        string='Travel',
    )
    date_time_delivery = fields.Datetime(
        string='Delivery date',
    )
    sequence = fields.Integer(
        help="Gives the sequence order.",
        default=1
    )
    distance_previous_point = fields.Float(
        string='Distance from previous point',
        digits=(16, 3),
    )
