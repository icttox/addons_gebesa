# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class TmsTravelGearCoast(models.Model):
    _name = 'tms.travel.gear.coast'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "begin_date_time desc"

    begin_date_time = fields.Datetime(
        string='From date',
    )
    begin_speed = fields.Float(
        string='Initial speed',
    )
    begin_latitude = fields.Float(
        required=False, digits=(20, 10),
        help='GPS begin latitude'
    )
    begin_longitude = fields.Float(
        required=False, digits=(20, 10),
        help='GPS begin longitude'
    )
    end_date_time = fields.Datetime(
        string='From date',
    )
    end_speed = fields.Float(
        string='Final speed',
    )
    end_latitude = fields.Float(
        required=False, digits=(20, 10),
        help='GPS end latitude'
    )
    end_longitude = fields.Float(
        required=False, digits=(20, 10),
        help='GPS end longitude'
    )
    distance = fields.Float(
        help='Distance'
    )
    duration = fields.Char(
        string='Duration',
    )
    max_speed = fields.Float(
        string='Max speed',
    )
    avg_speed = fields.Float(
        string='Avg Speed',
    )
    travel_id = fields.Many2one(
        'tms.travel',
        string='Travel',
    )
