# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    segment_line_ids = fields.One2many(
        'mrp.segment.line',
        'mrp_production_id',
        string='Segments line',
    )
    segment = fields.Char(
        string='Segment',
        compute='_compute_segment_name',
        store=True,
    )

    @api.depends('segment_line_ids')
    def _compute_segment_name(self):
        for production in self:
            segment = ''
            for line in production.segment_line_ids:
                segment += line.segment_id.folio + ','
            production.segment = segment[:-1]



# class MrpProductionProductLine(models.Model):
#     _inherit = 'mrp.production.product.line'

#     standard_cost = fields.Float(
#         string=_('Standard Cost'),
#         compute='_compute_standard_price',
#         store=True,
#         readonly=True,
#     )
#     location_id = fields.Many2one(
#         'stock.location',
#         string='Source location',
#     )

#     @api.depends('product_id')
#     def _compute_standard_price(self):
#         for line in self:
#             line.standard_cost = line.product_id.standard_price


# class MrpBom(models.Model):
#     _inherit = 'mrp.bom'

#     @api.model
#     def _prepare_consume_line(self, bom_line_id, quantity):
#         res = super(MrpBom, self)._prepare_consume_line(bom_line_id, quantity)
#         res['location_id'] = bom_line_id.location_id.id
#         return res
