# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    segment_status = fields.Selection(
        [('no_segment', 'No Segment'),
         ('partial_segment', 'Partial Segment'),
         ('total_segment', 'Total Segment')],
        string="Segment Status",
        default='no_segment',
        store=True,
    )

    related_segment = fields.Char(
        string='Relatad Segment',
        default='',
    )
    production_status = fields.Selection(
        [('no_production', 'No Production'),
         ('partial_production', 'Partial Production'),
         ('total_production', 'Total Production')],
        string="Production Status",
        default='no_production',
        compute='_compuete_production_status',
        store=True,
    )

    @api.model
    def _prepare_procurement_values(self):
        res = super(SaleOrder, self)._prepare_procurement_group()
        res['sale_id'] = self.id
        return res

    @api.depends('order_line.segment_qty')
    def _compuete_production_status(self):
        for sale in self:
            seg_qty = 0
            pro_qty = 0
            for line in sale.order_line:
                seg_qty += line.segment_qty
                pro_qty += line.product_uom_qty
            if seg_qty == pro_qty:
                sale.production_status = 'total_production'
            elif seg_qty == 0:
                sale.production_status = 'no_production'
            else:
                sale.production_status = 'partial_production'


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    segment_qty = fields.Float(
        string='Segmented quantity',
    )
