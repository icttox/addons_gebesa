# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class StockPicking(models.Model):
    _name = 'stock.picking'
    _inherit = 'stock.picking'

    sale_id = fields.Many2one('sale.order',
                              string='Sale Order',
                              store=True,)
    cust_ven_id = fields.Many2one(
        related='sale_id.partner_id',
        string='Customer',
        store=True,
    )
    client_order_ref = fields.Char(
        related='sale_id.client_order_ref',
        string='Customer ref',
        store=True,
    )

    sale_cost_id = fields.Many2one(
        'sale.order',
        string=("Costo pertenece a pedido"),
    )

    @api.multi
    def copy(self, default=None):
        if 'backorder_id' not in default:
            for picking in self:
                # Este if es para las devoluciones de cleintes
                if picking.location_id.usage == 'customer' or picking.location_dest_id.usage == 'customer':
                    continue
                if picking.sale_id:
                    raise ValidationError(
                        "No puede duplicar un movimiento de pedido")
        return super().copy(default)
