# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64
from io import StringIO
from odoo import api, models
from odoo.exceptions import ValidationError
from odoo.addons.report_tags.models import code128


class ParticularReport(models.AbstractModel):
    _name = 'report.report_tags.report_tag1_2_4'
    _description = 'Report Tags 2x4'

    @api.model
    def code128_format(self, data):
        return code128.code128_format(data)

    @api.model
    def code128_image(self, data):
        image_new = code128.code128_image(data)
        buffer = StringIO.StringIO()
        image_new.save(buffer, format="JPEG")
        return base64.b64encode(buffer.getvalue())

    @api.multi
    def _get_report_values(self, docids, data=None):
        self.model = 'sale.order'
        order = self.env[self.model].browse(docids)
        cust_obj = self.env['product.product.customer']
        code_customer = {}

        for sale in order:
            for line in sale.order_line:
                cusmtomer_code = cust_obj.search(
                    [('product_id', '=', line.product_id.id),
                     ('partner_id', '=', sale.partner_id.id)])
                if not cusmtomer_code:
                    raise ValidationError(
                        "The product %s does not have code for this client %s"
                        % (line.product_id.name, sale.partner_id.name))
                code_customer[line.id] = cusmtomer_code
        docargs = {
            'doc_ids': docids,
            'doc_model': self.model,
            'docs': order,
            'code_customer': code_customer,
            'code128_format': self.code128_format,
            'code128_image': self.code128_image,
        }
        return docargs
