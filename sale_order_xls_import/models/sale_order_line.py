# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    rep_sale_id = fields.Many2one(
        'sale.order',
        string='Reposition sale Order',
    )

    rep_sale_line_id = fields.Many2one(
        'sale.order.line',
        string='Reposition sale Order Line',
    )
