# Copyright 2023, Cesar Barron
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    sale_order_line_ids = fields.Many2many(
        'sale.order.line',
        'mrp_production_sale_line_rel',
        'production_id',
        'sale_line_id',
        string='Sale order lines',
        copy=False,
    )

    sale_order_ids = fields.Many2many(
        'sale.order',
        'mrp_production_sale_rel',
        'production_id',
        'sale_id',
        string='Sale orders',
        copy=False,
    )

    partner_ids = fields.Many2many(
        'res.partner',
        'mrp_production_partner_rel',
        'production_id',
        'partner_id',
        string='Partners',
        copy=False,
    )

    procurement_location_id = fields.Many2one(
        'stock.location',
        related='rule_id.location_id',
        string='Procurement location',
        store=True
    )
    sale_line_qty_info = fields.Char(
        string='Info Sale Line qty',
        copy=False,
    )


class MrpProductProduce(models.TransientModel):
    _inherit = "mrp.product.produce"

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)

        if self._context and self._context.get('active_id'):
            production = self.env['mrp.production'].browse(self._context['active_id'])
            serial_finished = (production.product_id.tracking == 'serial')
            if not serial_finished:
                main_product_moves = production.move_finished_ids.filtered(
                    lambda x: x.product_id.id == production.product_id.id and x.state == 'cancel')
                if 'product_qty' in fields:
                    res['product_qty'] = res['product_qty'] - sum(main_product_moves.mapped('product_uom_qty'))

        return res
