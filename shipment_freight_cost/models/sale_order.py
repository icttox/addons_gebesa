# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    inv_rel_so_ids = fields.One2many(
        'inv.rel.so',
        'order_id',
        string='Order'
    )
