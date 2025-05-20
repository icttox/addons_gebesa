# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class SaleOrderLine(models.Model):
    _name = 'sale.order.line'
    _inherit = 'sale.order.line'

    netsuite_line = fields.Integer(
        'Line Netsuite',
        help='Line number in Netsuite',
    )

    options = fields.Char(
        string='Options',
        size=100,
        help='Options',
    )
