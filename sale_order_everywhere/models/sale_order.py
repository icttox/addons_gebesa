# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    sale_everywhere = fields.Boolean(
        string='Sale Everywhere',
    )

    @api.multi
    def sale_order_everywhere(self):
        self._cr.execute("""
            UPDATE sale_order SET sale_everywhere = False
            WHERE sale_everywhere IS True
            AND id IN (
                SELECT order_id FROM sale_order_line
                WHERE id IN (
                    SELECT sale_line_id FROM mrp_production
                    WHERE sale_line_id IS NOT NULL AND sale_id IS NULL))
        """)

        order_ids = self.search([
            ('state', 'in', ['done', 'sale']),
            ('sale_everywhere', '!=', True)
        ])
        for sale in order_ids:
            self._cr.execute("""
                UPDATE stock_move AS sm SET
                    sale_id = so.id,
                    cust_ven_id = so.partner_id,
                    client_order_ref = so.client_order_ref
                FROM sale_order_line AS sol
                JOIN sale_order AS so ON sol.order_id = so.id
                WHERE sol.order_id = %s AND sm.sale_line_id = sol.id
                """, (sale.id,))

            self._cr.execute("""
                UPDATE stock_picking AS sp SET
                    cust_ven_id = so.partner_id,
                    client_order_ref = so.client_order_ref
                FROM sale_order AS so
                WHERE so.id = %s AND sp.sale_id = so.id
                """, (sale.id,))

            self._cr.execute("""
                UPDATE mrp_production AS mp SET
                    sale_id = so.id,
                    partner_id = so.partner_id,
                    client_order_ref = so.client_order_ref,
                    city_shipping = rp.city,
                    warehouse_id = so.warehouse_id,
                    partner_dealer_id = so.partner_dealer_id
                FROM sale_order_line AS sol
                JOIN sale_order AS so ON sol.order_id = so.id
                JOIN res_partner AS rp ON so.partner_shipping_id = rp.id
                WHERE sol.order_id = %s AND mp.sale_line_id = sol.id
                """, (sale.id,))

            sale.sale_everywhere = True

    # @api.multi
    # def action_confirm(self):
    #     # group_obj = self.env['procurement.group']
    #     # move_obj = self.env['stock.move']
    #     res = super(SaleOrder, self).action_confirm()
    #     for order in self:
    #         # # group = group_obj.search([('sale_id', '=', order.id)])
    #         # # for procurement in group.procurement_ids:
    #         # #     procurement.sale_id = group.sale_id
    #         # #     if procurement.production_id:
    #         # #         procurement.production_id.sale_id = group.sale_id
    #         # # moves = move_obj.search([('group_id', '=', group.id)])
    #         # # for move in moves:
    #         # #     move.sale_id = group.sale_id

    #         # if not order.dealer_id:
    #         #     dealer = None
    #         # else:
    #         #     dealer = order.dealer_id.id
    #         # self._cr.execute('UPDATE mrp_production mp SET dealer_id = %s '
    #         #                  'FROM procurement_group pg '
    #         #                  'WHERE pg.sale_id = %s AND pg.id = mp.procurement_group_id',
    #         #                  (dealer, order.id,))
    #         self._cr.execute("""
    #             UPDATE stock_move AS sm SET
    #                 sale_id = so.id,
    #                 cust_ven_id = so.partner_id,
    #                 client_order_ref = so.client_order_ref
    #             FROM sale_order_line AS sol
    #             JOIN sale_order AS so ON sol.order_id = so.id
    #             WHERE sol.order_id = %s
    #             """ % (order.id))
    #     return res
