# Copyright 2020, Samuel Barron
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class StockWarehouseOrderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    week_min_inv = fields.Float(
        string='Weeks of Minimum Inventory',
    )
    week_max_inv = fields.Float(
        string='Weeks of Maximum Inventory',
    )

    @api.constrains('week_min_inv', 'week_max_inv')
    def _check_description(self):
        for orderpoint in self:
            if orderpoint.week_min_inv > orderpoint.week_max_inv:
                raise Warning('The minimum weeks must be less than the maximum weeks')
            if orderpoint.week_min_inv < 0 or orderpoint.week_max_inv < 0:
                raise Warning('You cannot have negative weeks')

    def calculate_order_point_weeks(self):
        orderpoint = self.search([
            ('week_min_inv', '>', 0.00),
            ('week_max_inv', '>', 0.00)
        ])

        for orp in orderpoint:
            week_amount = orp.product_id._get_weekly_consume(
                3, orp.location_id.id)

            orp.write({
                'product_min_qty': int(orp.week_min_inv * week_amount),
                'product_max_qty': int(orp.week_max_inv * week_amount),
            })
