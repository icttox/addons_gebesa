# -*- coding: utf-8 -*-
# © 2021, Leslie Marquez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import base64
from io import StringIO
from odoo import api, models
from odoo.exceptions import ValidationError
from odoo.addons.report_tags.models import code128


class ParticularReport(models.AbstractModel):
    _name = 'report.report_tags.report_tag_prod_2_4_sin_barcode'
    _description = 'Report Tags Prod 2X4 sin barcode'

    @api.model
    def code128_format(self, data):
        return code128.code128_format(data)

    @api.model
    def code128_image(self, data):
        image_new = code128.code128_image(data)
        buffer = StringIO.StringIO()
        image_new.save(buffer, format="JPEG")
        return base64.b64encode(buffer.getvalue())

    def get_customer_code(self, productions):
        code_customer = {}

        for prod in productions:
            customer_code = self.env['product.product.customer'].search([('product_id', '=', prod.product_id.id), ('partner_id', '=', prod.partner_id.id)])
            if not customer_code:
                raise ValidationError("The product %s does not have code for this client %s" % (prod.product_id.name, prod.partner_id.name))
            code_customer[prod.id] = {
                'customer_code': customer_code,
                'partner_id': prod.partner_id
            }
        return code_customer

    @api.multi
    def _get_report_values(self, docids, data=None):
        self.model = 'mrp.production'
        production = self.env[self.model].browse(docids)
        cust_obj = self.env['product.product.customer']
        
        code_customer = self.get_customer_code(production)
        docargs = {
            'doc_ids': docids,
            'doc_model': self.model,
            'docs': production,
            'code_customer': code_customer,
            'code128_format': self.code128_format,
            'code128_image': self.code128_image,
        }
        return docargs
