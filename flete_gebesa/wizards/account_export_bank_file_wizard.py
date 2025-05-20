# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import io
import json
import base64
from odoo import api, fields, models
import xlwt


class AccountExportBankFileWizard(models.TransientModel):
    _name = 'account.export.bank.file.wizard'
    _description = 'descripcion pendiente'

    ref = fields.Char(
        string='Reference',
    )

    report_attach = fields.Binary(
        attachment=True,
        string="File CSV")

    @api.multi
    def export_file(self):
        move_line_ids = self.env['account.move.line'].browse(
            self._context.get('active_ids'))
        buffer_io = io.BytesIO()
        book = xlwt.Workbook()
        sheet = book.add_sheet("sheet")
        row = 0

        for line in move_line_ids:
            if not line.currency_id:
                currency = 1
            elif line.currency_id.name == 'MXN':
                currency = 1
            elif line.currency_id.name == 'USD':
                currency = 2
            else:
                currency = 0

            row_sheet = sheet.row(row)
            row_sheet.write(0, row + 1)
            row_sheet.write(1, str(line.journal_id.bank_acc_number).zfill(10))
            row_sheet.write(2, line.acc_number)
            row_sheet.write(3, "%.*f" % (2, line.credit))
            row_sheet.write(4, currency)
            row_sheet.write(5, line.move_id.name.replace('/', ''))
            row += 1

        row_sheet = sheet.row(row)
        row_sheet.write(0, 1)
        row_sheet.write(1, row)
        row_sheet.write(2, self.ref[:1])

        book.save(buffer_io)
        result = buffer_io.getvalue()
        self.report_attach = base64.encodestring(result)

        return {
            'type': 'ir.actions.act_url',
            'url': self.get_compose_download_url(
                self.ref + '.xls'),
            'target': 'new',
        }

    def get_compose_download_url(self, filename, download=True):
        base_url = ("/web/content/{model}/{res_id}/report_attach/{filename}"
                    "?download={download}")
        return base_url.format(
            model=self._name, res_id=self.id, filename=filename,
            download=json.dumps(download))
