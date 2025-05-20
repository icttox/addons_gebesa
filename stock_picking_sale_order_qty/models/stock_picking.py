# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def count_product_bom_panthom(self, bom):
        bom_obj = self.env['mrp.bom']
        bom_product = {}
        for line in bom.bom_line_ids:
            product = line.product_id
            line_bom = bom_obj.search([
                ('product_id', '=', product.id),
                ('active', '=', True)
            ])
            if line_bom.type == 'phantom':
                bom_line_product = self.count_product_bom_panthom(line_bom)
                for b_line in bom_line_product:
                    qty = line.product_qty * bom_line_product[b_line]
                    if b_line in bom_product:
                        bom_product[b_line] += qty
                    else:
                        bom_product[b_line] = qty
            else:
                qty = bom.product_qty * line.product_qty
                if line.product_id.id in bom_product:
                    bom_product[line.product_id.id] += qty
                else:
                    bom_product[line.product_id.id] = qty
        return bom_product

    # @api.multi
    # def button_validate(self):
    #     bom_obj = self.env['mrp.bom']
    #     product_obj = self.env['product.product']
    #     for pick in self:
    #         if pick.location_dest_id.usage != 'customer':
    #             continue
    #         if not pick.sale_id:
    #             continue
    #         if pick.sale_id.id in (1627, 1628, 1629, 2770, 859, 3140, 3342,
    #                                3430, 3597, 3588, 3584, 3579, 3909) or pick.sale_id.sale_picking_adm is True:
    #             continue
    #         products = {}
    #         for line in pick.sale_id.order_line:
    #             product = line.product_id
    #             bom = bom_obj.search([
    #                 ('product_id', '=', product.id),
    #                 ('active', '=', True)
    #             ])
    #             if bom.type == 'phantom':
    #                 continue
    #             else:
    #                 qty = line.product_uom_qty
    #                 if line.product_id.id in products.keys():
    #                     products[line.product_id.id] += qty
    #                 else:
    #                     products[line.product_id.id] = qty
    #         for move in pick.move_lines_related:
    #             if move.product_id.id in products.keys():
    #                 products[move.product_id.id] -= move.product_uom_qty
    #         backorder = pick.backorder_id
    #         while backorder:
    #             for move in backorder.move_lines_related:
    #                 if move.product_id.id in products.keys():
    #                     products[move.product_id.id] -= move.product_uom_qty
    #             backorder = backorder.backorder_id
    #         for prod in products:
    #             if products[prod] != 0:
    #                 product = product_obj.browse([prod])
    #                 # No borrar este código comentado, do not erase commented code below
    #                 # raise UserError(_('Missing %s %s') % (
    #                 #     products[prod], product.name))
    #     return super(StockPicking, self).button_validate()
