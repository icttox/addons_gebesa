# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models
from odoo.exceptions import ValidationError


class ParticularReport(models.AbstractModel):
    _name = 'report.report_tags.report_customer_code_so_tag'
    _description = 'Report Tags customer code SO'

    @api.multi
    def _get_report_values(self, docids, data=None):
        self.model = 'sale.order'
        order_ids = self.env[self.model].browse(docids)
        cust_obj = self.env['product.product.customer']
        cust_code = {}
        for order in order_ids:
            cust_code[order.id] = {}
            for line in order.order_line:
                cusmtomer_code = cust_obj.search(
                    [('product_id', '=', line.product_id.id),
                     ('partner_id', '=', order.partner_id.id)])
                if not cusmtomer_code:
                    raise ValidationError(
                        "Al producto %s le falta el codigo para el cliente %s"
                        % (line.product_id.default_code, order.partner_id.name))
                    # continue
                cust_code[order.id][line.product_id.id] = cusmtomer_code
        docargs = {
            'doc_ids': docids,
            'doc_model': self.model,
            'docs': order_ids,
            'cust_code': cust_code,
        }

        return docargs
