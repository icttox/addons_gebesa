# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ParticularReport(models.AbstractModel):
    _name = 'report.report_tags.report_tag_winholt_tabloide'
    _description = 'Report Tags Winholt tabloide'

    @api.multi
    def _get_report_values(self, docids, data=None):
        self.model = 'sale.order'
        order_ids = self.env[self.model].browse(docids)
        renglones = []
        ren = []
        count = 0
        for order in order_ids:
            for line in order.order_line:
                for num in range(int(line.product_uom_qty)):
                    if count < 7:
                        ren.append(line.product_id)
                    else:
                        renglones.append(ren)
                        ren = []
                        ren.append(line.product_id)
                        count = 0
                    count = count + 1
        docargs = {
            'doc_ids': docids,
            'doc_model': self.model,
            'docs': order_ids,
            'renglones': renglones,
            'partner_id': order_ids[0].partner_id
        }
        return docargs
