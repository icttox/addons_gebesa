# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    sale_id = fields.Many2one(
        'sale.order',
        string='Sale order',
        # related='sale_line_id.order_id',
        # store=True,
    )
    cust_ven_id = fields.Many2one(
        'res.partner',
        # related='sale_id.partner_id',
        string='Customer',
        # store=True,
    )
    client_order_ref = fields.Char(
        # related='sale_id.client_order_ref',
        string='Customer ref',
        # store=True,
    )

    def _prepare_procurement_values(self):
        # self.ensure_one()
        res = super()._prepare_procurement_values()
        res['sale_line_id'] = self.sale_line_id.id
        # res['sale_line_obj'] = self.sale_line_id
        # res['sale_id'] = self.sale_line_id.order_id.id
        # res['cust_ven_id'] = self.sale_line_id.order_id.partner_id.id
        # res['client_order_ref'] = self.sale_line_id.order_id.client_order_ref

        return res

    # def _get_new_picking_values(self):
    #     vals = super(StockMove, self)._get_new_picking_values()
    #     vals['cust_ven_id'] = self.sale_line_id.order_id.partner_id.id
    #     vals['client_order_ref'] = self.sale_line_id.order_id.client_order_ref
    #     return vals
