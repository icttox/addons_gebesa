# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ParticularReport(models.AbstractModel):
    _name = 'report.report_tags.report_tag_segment'
    _description = 'Report Tag Segment'

    @api.multi
    def _get_report_values(self, docids, data=None):
        self.model = 'mrp.segment'
        segment = self.env[self.model].browse(docids)
        logo = self.env.user.company_id.logo
        # production = []
        production_id = segment.mapped('line_ids').mapped(
            'mrp_production_id').mapped('id')
        # tag_line = {}
        # for seg in segment:
        #     for line in seg.line_ids:
        #         production.append(line.mrp_production_id)
        #         move = line.mrp_production_id.move_prod_id.move_dest_id
        #         if move.location_dest_id.usage in ('customer', 'transit'):
        #             if move.location_dest_id.usage == 'transit':
        #                 move = move.move_dest_id.move_dest_id
        #             if move.procurement_id and move.procurement_id.sale_line_id:
        #                 tag_line[line.mrp_production_id.id] = (
        #                     move.procurement_id.sale_line_id.line_tag_number)
        docargs = {
            'doc_ids': production_id,
            'doc_model': self.model,
            'docs': self.env['mrp.production'].browse(production_id),
            # 'tag_line': tag_line,
            'logo': logo,
        }

        return docargs
