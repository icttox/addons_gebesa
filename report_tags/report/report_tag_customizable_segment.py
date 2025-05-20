# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models
from odoo.exceptions import ValidationError


class ParticularReport(models.AbstractModel):
    _name = 'report.report_tags.report_tag_customizable_segment'
    _description = 'Report Tags customizable segment'

    @api.multi
    def _get_report_values(self, docids, data=None):
        self.model = 'mrp.segment'
        segment = self.env[self.model].browse(docids)
        customer_obj = self.env['product.product.customer']
        lang_obj = self.env['res.lang']
        production = []
        langs = []
        translates = {}
        for seg in segment:
            for line in seg.line_ids:
                prod = line.mrp_production_id
                production.append(prod)
                translates[prod.id] = customer_obj.search(
                    [('product_id', '=', prod.product_id.id),
                     ('partner_id', '=', prod.partner_id.id)],
                    limit=1)
                if not translates[prod.id]:
                    raise ValidationError(
                        "The product %s does not have code for this client" % (
                            prod.product_id.name))
        lang = lang_obj.search([('active', '=', True)])
        langs = []
        for lan in lang:
            langs.append(lan.code)
        docargs = {
            'doc_ids': docids,
            'doc_model': self.model,
            'docs': production,
            'translates': translates,
            'langs': langs,
        }

        return docargs
