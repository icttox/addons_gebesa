# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ParticularReport(models.AbstractModel):
    _name = 'report.report_tags.report_customer_code_tag'
    _description = 'Report Tags customer code'

    @api.multi
    def _get_report_values(self, docids, data=None):
        self.model = 'mrp.segment'
        segment = self.env[self.model].browse(docids)
        cust_obj = self.env['product.product.customer']
        production = []
        cusmtomer_codes = {}

        for seg in segment:
            for line in seg.line_ids:
                pro = line.mrp_production_id
                cusmtomer_code = cust_obj.search(
                    [('product_id', '=', pro.product_id.id),
                     ('partner_id', '=', pro.partner_id.id)])
                if not cusmtomer_code:
                    # raise ValidationError(
                    #    "The product %s does not have code for this client %s"
                    #    % (pro.product_id.name, pro.partner_id.name))
                    continue
                cusmtomer_codes[pro.id] = cusmtomer_code
                production.append(pro.id)
        docargs = {
            'doc_ids': production,
            'doc_model': self.model,
            'docs': self.env['mrp.production'].browse(production),
            'cusmtomer_codes': cusmtomer_codes,
        }

        return docargs
