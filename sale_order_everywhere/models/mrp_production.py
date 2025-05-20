# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    sale_line_id = fields.Many2one(
        'sale.order.line',
        string='Sale Line',
        copy=False,
    )
    sale_id = fields.Many2one(
        'sale.order',
        string='Sale order',
        copy=False,
        # related='sale_line_id.order_id',
        # store=True,
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        copy=False,
        # related='sale_id.partner_id',
        # store=True,
    )
    client_order_ref = fields.Char(
        string='Customer ref',
        copy=False,
        # related='sale_id.client_order_ref',
        # store=True,
    )
    city_shipping = fields.Char(
        string='City',
        copy=False,
        # related='sale_id.partner_shipping_id.city',
        # store=True,
    )
    warehouse_id = fields.Many2one(
        'stock.warehouse',
        string='Warehouse',
        # related='sale_id.warehouse_id',
        # store=True,
    )

    def _generate_finished_moves(self):
        ctx = dict(
            self._context,
            default_sale_line_id=self.sale_line_id.id,
        )
        contextual_self = self.with_context(ctx)
        res = super(MrpProduction, contextual_self)._generate_finished_moves()
        return res

    def _generate_raw_moves(self, lines):
        ctx = dict(
            self._context,
            default_sale_line_id=self.sale_line_id.id,
        )
        contextual_self = self.with_context(ctx)
        res = super(MrpProduction, contextual_self)._generate_raw_moves(lines)
        return res
