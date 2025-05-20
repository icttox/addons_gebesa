# Copyright 2023, Samuel Barron
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import logging
from odoo import models

_logger = logging.getLogger(__name__)


def copy_format(book, fmt):
    properties = [f[4:] for f in dir(fmt) if f[0:4] == 'set_']
    dft_fmt = book.add_format()
    res = book.add_format(
        {k: v for k, v in fmt.__dict__.items() if k in properties and dft_fmt.__dict__[k] != v})
    return res


class UsmcaFormatXlsx(models.AbstractModel):
    _name = 'report.website_lunch_hr.report_employee_barcode_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, objects):
        workbook.set_properties({
            'comments': 'Created with Python and XlsxWriter from Odoo 12.0'})
        row_format = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'font_size': 14,
        })
        barcode_format = workbook.add_format({
            'valign': 'vcenter',
            'align': 'center',
            'font': 'CCode39',
            'font_size': 14,
        })

        for company in objects.mapped('company_id'):
            sheet = workbook.add_worksheet(company.name)
            emp_company = objects.filtered(
                lambda employee: employee.company_id.id == company.id)
            count = 1
            sheet.set_portrait()
            sheet.fit_to_pages(1, 0)
            sheet.set_zoom(100)

            sheet.set_column(0, 0, 40)
            sheet.set_column(1, 1, 20)
            sheet.set_column(2, 3, 40)

            for employee in emp_company:
                sheet.write('A' + str(count), employee.name, row_format)
                sheet.write('A' + str(count + 1), employee.consecutive_id, row_format) if employee.consecutive_id else ''
                password = employee.decrypt_password_as_string(employee.id) if employee.lunch_pass else ''

                barcode = '*' + str(employee.identification_id) + '-' + password + '*' if employee.identification_id and password else ''

                sheet.write('A' + str(count + 2), barcode, barcode_format)
                count = count + 4
