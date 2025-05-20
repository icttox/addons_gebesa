# -*- coding: utf-8 -*-
# Copyright YEAR(S), AUTHOR(S)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class MrpShipment(models.Model):

    _inherit = 'mrp.shipment'

    carrier_name = fields.Char(string='Carrier name')

    trailer_number = fields.Char(string='Trailer number')

    special_delivery_instructions = fields.Text(
        string='Special Delivery Instructions',
    )

    seal = fields.Char(
        string='Seal',
    )

    partner_id = fields.Many2one(
        'res.partner',
        string='For',
    )

    date_positioning = fields.Date(
        string='Positioning(date)',
    )

    time_positioning = fields.Char(
        string='Positioning(time)',
    )

    team = fields.Char(
        string='Team:',
    )

    mercancia = fields.Char(
        string='Mercancia:',
    )

    maniobras = fields.Boolean(
        string='Maniobras:',
    )
