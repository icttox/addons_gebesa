# -*- coding: utf-8 -*-
# © 2017 Aldo Nerio
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64
from io import BytesIO
from odoo import fields, models, api
from odoo.addons.report_tags.models import code128
# from io import StringIO


class ProductProductCustomer(models.Model):
    _inherit = 'product.product.customer'

    code_128c = fields.Char(
        string='Filed Label',
        compute='_calculo_code_128b',
        store=True,
    )

    code_128_bina = fields.Binary(
        string='Filed Label',
        compute='_calculo_code_128b',
        store=True,
    )
    version = fields.Char(
        string='Version',
    )
    bc_value = fields.Char(
        string='Barcode value',
    )

    pack_num = fields.Integer(
        string='Numero paquetes',
        default=1
    )

    @api.depends('customer_code')
    def _calculo_code_128b(self):
        for record in self:
            record.code_128c = code128.code128_format(record.customer_code)
            image_new = code128.code128_image(record.customer_code)
            # buffer = StringIO.StringIO()
            buffer = BytesIO()
            image_new.save(buffer, format="JPEG")
            record.code_128_bina = base64.b64encode(buffer.getvalue())
        return True
