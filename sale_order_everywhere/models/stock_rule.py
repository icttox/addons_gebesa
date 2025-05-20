# -*- coding: utf-8 -*-
# Copyright YEAR(S), AUTHOR(S)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _prepare_mo_vals(self, product_id, product_qty, product_uom,
                         location_id, name, origin, values, bom):
        res = super(StockRule, self)._prepare_mo_vals(
            product_id, product_qty, product_uom, location_id,
            name, origin, values, bom)

        # sale_line_id = values['sale_line_obj']
        res['sale_line_id'] = values['sale_line_id']
        # res['sale_id'] = sale_line_id.order_id.id
        # res['partner_id'] = sale_line_id.order_id.partner_id.id
        # res['client_order_ref'] = sale_line_id.order_id.client_order_ref
        # res['city_shipping'] = sale_line_id.order_id.partner_shipping_id.city
        # res['warehouse_id'] = sale_line_id.order_id.warehouse_id.id
        if 'group_id' in values and values['group_id']:
            res['procurement_group_id'] = values['group_id'].id

        return res

    # def _get_custom_move_fields(self):
    #     fields = super(StockRule, self)._get_custom_move_fields()
    #     # fields += ['sale_id', 'cust_ven_id', 'client_order_ref']
    #     fields += ['sale_id']
    #     return fields
