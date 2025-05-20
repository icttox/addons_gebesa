# -*- coding: utf-8 -*-
# Copyright 2012, Israel Cruz Argil, Argil Consulting
# Copyright 2016, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    expense_currency_rate = fields.Float()

    usuariogps = fields.Char(
        string='Usuario')

    passwordgps = fields.Char(
        string='Password')

    urlecho = fields.Char(
        string='URL ECHO')

    tms_product_id = fields.Many2one(
        'product.product',
        string='Product',
    )

    tms_location_id = fields.Many2one(
        'stock.location',
        string='Origin Location',
    )

    tms_location_dest_id = fields.Many2one(
        'stock.location',
        string='Destination Location',
    )

    tms_type_adjustment_id = fields.Many2one(
        'type.adjustment',
        string='Type Adjustment',
    )

    tms_type_adjustment_ret_id = fields.Many2one(
        'type.adjustment',
        string='Type of adjustment (return)',
    )
