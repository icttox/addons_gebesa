# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class FuelHistoryPrice(models.Model):
    _name = 'fuel.history.price'
    _inherit = ['mail.thread']
    _description = "Fuel History Price"
    _order = 'date asc'
    _rec_name = 'date'

    date = fields.Date(
        string='Date',
        default=fields.Date.today,
        required=True,
        track_visibility='always')

    price = fields.Float(
        string='Fuel Price',
        required=True,
        track_visibility='always'
    )

    fuel_type = fields.Selection(
        [('magna', 'Magna'),
            ('premium', 'Premium'),
            ('diesel', 'Diesel')],
        string="Fuel Type",
        default='diesel',
        track_visibility='always'
    )
