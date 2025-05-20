# -*- coding: utf-8 -*-
# © 2017 Aldo Nerio
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import io
import json
import base64
from odoo import _, fields, models, api
import xlwt


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    bom_line_product_value_ids = fields.One2many(
        'mrp.bom.product.replacement',
        'bom_line_value_id',
        string='BoM line replacements',
        copy=False,
    )

    fixed = fields.Boolean(
        string='Fijo',
    )

    report_attach = fields.Binary(
        attachment=True,
        string="Product Replacement Xsl")

    def fields_columns(self):
        fields_column = {
            'En_Producto': 0,
            'Nombre_Variante': 1,
            'Reemplazar_Con': 2,
            'Nombre_Reemplazo': 3,
        }
        return fields_column

    def write_columns_xls(self, row_sheet, fmt, col1):
        row_sheet.write(0, col1, fmt)

    @api.multi
    def action_get_product_variants(self):

        products = self.env['product.product'].search(
            [('product_tmpl_id', '=', self.bom_id.product_tmpl_id.id)])

        res = {}

        self.bom_line_product_value_ids.unlink()

        for product in products:
            if product == self.bom_id.product_id:
                continue

            res[product.id] = {
                'bom_line_value_id': self.id,
                'bom_product_id': product.id,
                'product_id': self.product_id
            }

        product_lines = self.bom_line_product_value_ids.browse([])

        for i in res.values():
            product_lines += product_lines.new(i)
        self.bom_line_product_value_ids = product_lines

    def action_export_replacement_list(self):
        result = []
        for line in self.bom_line_product_value_ids:
            result.append(
                {
                    'En_Producto': line.bom_product_id.default_code,
                    'Nombre_Variante': line.bom_product_id.product_tmpl_id.name,
                    'Reemplazar_Con': line.product_id.default_code,
                    'Nombre_Reemplazo': line.product_id.product_tmpl_id.name,
                })
        return self.export_result(result)

    def export_result(self, result):
        fields_columns = self.fields_columns()

        buffer_io = io.BytesIO()
        book = xlwt.Workbook()
        sheet = book.add_sheet("sheet")
        row = 0
        header_fields = list(fields_columns.keys())
        for key in header_fields:
            col = fields_columns.get(key) or 0
            head_name = key
            sheet.write(0, col, head_name)

        for element in result:
            row += 1
            row_sheet = sheet.row(row)

            for key, col in fields_columns.items():
                row_sheet.write(col, element[key])
        book.save(buffer_io)
        report = buffer_io.getvalue()
        self.report_attach = base64.encodestring(report)
        return {
            'type': 'ir.actions.act_url',
            'url': self.get_compose_download_url(
                _("ProductReplacement_") + self.bom_id.product_id.default_code.replace('/', '-') + '-' + self.product_id.default_code.replace('/', '-') + '.xls'),
            'target': 'new',
        }

    def get_compose_download_url(self, filename, download=True):
        base_url = ("/web/content/{model}/{res_id}/report_attach/{filename}"
                    "?download={download}")
        return base_url.format(
            model=self._name, res_id=self.id, filename=filename,
            download=json.dumps(download))
