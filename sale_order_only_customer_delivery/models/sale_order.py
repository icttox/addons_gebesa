# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    only_customer_delivery = fields.Boolean(
        string='Only customer delivery',
        default=False,
        copy=False
    )
