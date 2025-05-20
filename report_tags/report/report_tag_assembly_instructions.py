# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models
from odoo.exceptions import ValidationError


class ParticularReport(models.AbstractModel):
    _name = 'report.report_tags.report_tag_assembly_instructions'
    _description = 'Report Tag Assembly Instructions'

    @api.multi
    def _get_report_values(self, docids, data=None):
        self.model = 'mrp.production'
        production = self.env[self.model].browse(docids)

        for prod in production:
            prod_link = prod.product_id.product_tmpl_id.product_document_ids.filtered(
                lambda doc_link: doc_link.product_type == 'manual')

            if not prod_link:
                raise ValidationError(
                    "The product [%s] %s does not have an instruction manual"
                    % (prod.product_id.default_code, prod.product_id.name))

        docargs = {
            'doc_ids': docids,
            'doc_model': self.model,
            'docs': production,
        }
        return docargs
