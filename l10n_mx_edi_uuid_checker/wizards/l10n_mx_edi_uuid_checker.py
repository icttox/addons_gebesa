# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import os
from base64 import b64decode
import io
import json
import base64
import xlwt

try:
    import xlrd
except ImportError:
    xlrd = None

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import pycompat


class UuidChecker(models.TransientModel):
    _name = "uuid.checker"
    _description = "UUID Checker"

    data = fields.Binary('File', required=True)
    filename = fields.Char('File Name', required=True)
    report_attach = fields.Binary(attachment=True, string="File XLS")

    def fields_columns(self):
        fields_column = {
            'ESTATUS ODOO': 0,
            'ESTATUS SAT': 1,
            'RFC': 2,
            'PROVEEDOR': 3,
            'CONCEPTOS': 4,
            'FECHA_EMISION': 5,
            'FECHA_TIMBRADO': 6,
            'TOTAL_EXCEL': 7,
            'FORMA_PAGO': 8,
            'MONEDA': 9,
            'FOLIO_ODOO': 10,
            'TOTAL_ODOO': 11,
            'UUID': 12,
            'SERIE': 13,
            'FOLIO': 14,
        }
        return fields_column

    def write_columns_xls(self, row_sheet, fmt, col1):
        row_sheet.write(0, col1, fmt)

    @api.multi
    def execute_compare(self):
        for file in self:
            fileformat = os.path.splitext(file.filename)[-1][1:].lower()
            if fileformat not in ('xls', 'xlsx'):
                raise UserError(_('Valid format is .xls'))
            book = xlrd.open_workbook(file_contents=b64decode(self.data))
            sheet = book.sheet_by_index(0)
            is_int = isinstance(sheet.nrows, pycompat.integer_types)
            nrows = sheet.nrows if (is_int and sheet.nrows > 0) else 0
            result = []
            for row in pycompat.imap(sheet.row, range(1, nrows)):
                domain = [('cfdi_uuid', '=ilike', row[9].value),
                          ('state', '!=', 'cancel')]
                invoice = self.env['account.invoice'].search(domain, limit=1)
                odoo_num = invoice.number if invoice else ''
                total = invoice.amount_total if invoice else 0.00

                if not invoice:
                    aml = False
                    domain = [('fiscal_id', '=ilike', row[9].value)]
                    cfdi = self.env['cfdi.cfdi'].search(domain, limit=1)
                    if cfdi:
                        aml = self.env['account.move.line'].search(
                            [('cfdi_id', '=', cfdi.id)], limit=1)
                        odoo_num = aml.move_id.name if aml else ''
                        total = aml.debit if aml else 0.00

                result.append(
                    {
                        'ESTATUS ODOO': 'Encontrado' if invoice or aml else 'No encontrado',
                        'ESTATUS SAT': row[2].value,
                        'RFC': row[17].value,
                        'PROVEEDOR': row[18].value,
                        'CONCEPTOS': row[20].value,
                        'FECHA_EMISION': row[13].value,
                        'FECHA_TIMBRADO': row[16].value,
                        'TOTAL_EXCEL': row[29].value,
                        'FORMA_PAGO': row[33].value,
                        'MONEDA': row[30].value,
                        'FOLIO_ODOO': odoo_num,
                        'TOTAL_ODOO': total,
                        'UUID': row[9].value,
                        'SERIE': row[11].value,
                        'FOLIO': row[12].value,
                    })
            return self.export_result(result)

    def export_result(self, result):
        fields_columns = self.fields_columns()

        buffer_io = io.BytesIO()
        book = xlwt.Workbook()
        sheet = book.add_sheet("sheet")
        row = 0
        header_fields = list(fields_columns.keys())
        date_format = xlwt.XFStyle()
        date_format.num_format_str = 'dd/MM/yyyy'
        for key in header_fields:
            col = fields_columns.get(key) or 0
            head_name = key
            sheet.write(0, col, head_name)

        for element in result:
            row += 1
            row_sheet = sheet.row(row)

            for key, col in fields_columns.items():
                if key in ('FECHA_EMISION', 'FECHA_TIMBRADO'):
                    row_sheet.write(col, element[key], date_format)
                else:
                    row_sheet.write(col, element[key])
        book.save(buffer_io)
        report = buffer_io.getvalue()
        self.report_attach = base64.encodebytes(report)
        return {
            'type': 'ir.actions.act_url',
            'url': self.get_compose_download_url(
                _("DataCredito") + '.xls'),
            'target': 'new',
        }

    def get_compose_download_url(self, filename, download=True):
        base_url = ("/web/content/{model}/{res_id}/report_attach/{filename}"
                    "?download={download}")
        return base_url.format(
            model=self._name, res_id=self.id, filename=filename,
            download=json.dumps(download))
