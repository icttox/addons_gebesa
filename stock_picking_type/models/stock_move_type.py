# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockMoveType(models.Model):
    _name = 'stock.move.type'
    _description = 'Type move of stock'
    _order = 'name asc'
    _rec_name = 'name'

    code = fields.Char(
        string='Code', size=5,
        help='Code',
        readonly=True,
    )
    name = fields.Char(
        string='Name', size=120,
        help='Process name',
        translate=True,
    )
    type = fields.Selection(
        [('input', 'Input'),
         ('output', 'Output'),
         ('internal', 'Internal')],
        string="Type of move",
    )
    company_id = fields.Many2one(
        'res.company', string='Company',
        help='Company'
    )
