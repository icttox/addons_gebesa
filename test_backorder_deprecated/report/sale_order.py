# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    sale_backorder_ids = fields.One2many(
        'sale.order.backorder',
        'order_id',
        string=_('Sale Order Backorder'))
