# Copyright 2024, Marco Esquivel
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class MrpSegment(models.Model):
    _inherit = 'mrp.segment'

    picking_ids = fields.One2many(
        'stock.picking',
        'segment_id',
        string='Picking',
    )

    @api.multi
    def validate_segment(self):
        res = super().validate_segment()
        for segment in self:
            for line in segment.line_ids:
                for sale in line.mrp_production_id.sale_order_ids:
                    if not sale.related_segment:
                        self.env.cr.execute(
                            """UPDATE sale_order
                                SET related_segment = %s
                                WHERE id = %s """,
                            (segment.folio + ', ', sale.id)
                        )
                    elif segment.folio not in sale.related_segment:
                        self.env.cr.execute(
                            """update sale_order
                                set related_segment = CONCAT(
                                    related_segment,%s)
                                where id = %s """,
                            (segment.folio + ', ', sale.id)
                        )
                    prod = self.env['mrp.production'].search(
                        [('sale_order_ids', '=', sale.id),
                         ('state', '!=', 'cancel')])
                    prod_seg = self.env['mrp.production'].search(
                        [('sale_order_ids', '=', sale.id),
                         ('state', '!=', 'cancel'),
                         ('segment_line_ids', '!=', False)])
                    if not prod_seg:
                        sale.segment_status = 'no_segment'
                    elif len(prod) == len(prod_seg):
                        sale.segment_status = 'total_segment'
                    else:
                        sale.segment_status = 'partial_segment'
        return res
