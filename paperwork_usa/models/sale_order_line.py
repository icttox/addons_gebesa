# -*- coding: utf-8 -*-
# Copyright YEAR(S), AUTHOR(S)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class SaleOrderLine(models.Model):

    _inherit = 'sale.order.line'

    dealer_order_line = fields.Integer(
        string='Daler order line',
        help='Number of  dealer order line'
    )

    line_tag_number = fields.Char(
        string='Line item tag number'
    )

    reference_code = fields.Char(
        string='Clave referencia',
    )
