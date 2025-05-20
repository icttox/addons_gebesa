# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models
from odoo.exceptions import UserError


class ParticularReport(models.AbstractModel):
    _name = 'report.report_tags.report_tag_po'
    _description = 'Report Tags PO'

    @api.multi
    def _get_report_values(self, docids, data=None):
        self.model = 'purchase.order'
        purchase = self.env[self.model].browse(docids)

        for product in purchase.order_line.mapped('product_id'):
            if not product.default_code:
                raise UserError(
                    ('El producto %s no coontiene un código' % product.name))

        docargs = {
            'doc_ids': docids,
            'doc_model': self.model,
            'docs': purchase,
        }
        return docargs
