# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    related_segment = fields.Char(
        string='Relatad Segment',
        default='',
    )


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    related_segment = fields.Char(
        string='Relatad Segment',
        related='order_id.related_segment'
    )
