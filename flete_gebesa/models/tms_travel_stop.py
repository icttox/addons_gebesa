# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class TmsTravelStop(models.Model):
    _name = 'tms.travel.stop'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "from_date desc"

    address = fields.Text(
        string='Address',
    )
    distance = fields.Float(
        help='Distance'
    )
    duration = fields.Char(
        string='Duration',
    )
    latitude = fields.Float(
        required=False, digits=(20, 10),
        help='GPS Latitude'
    )
    longitude = fields.Float(
        required=False, digits=(20, 10),
        help='GPS Longitude'
    )
    from_date = fields.Datetime(
        string='From date',
    )
    to_date = fields.Datetime(
        string='From date',
    )
    unit_name = fields.Char(
        string='Unit name',
    )
    travel_id = fields.Many2one(
        'tms.travel',
        string='Travel',
    )
