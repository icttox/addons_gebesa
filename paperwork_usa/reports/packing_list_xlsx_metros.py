# Copyright 2021, Samuel Barron
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import base64
import io
from odoo import fields, models, tools
from odoo.tools.translate import _
from odoo.modules.module import get_module_resource


def copy_format(book, fmt):
    properties = [f[4:] for f in dir(fmt) if f[0:4] == 'set_']
    dft_fmt = book.add_format()
    res = book.add_format(
        {k: v for k, v in fmt.__dict__.items() if k in properties and dft_fmt.__dict__[k] != v})
    return res


class PackingListXlsxMetros(models.AbstractModel):
    _name = 'report.paperwork_usa.packing_list_xlsx_metros'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, objects):
        workbook.set_properties({
            'comments': 'Created with Python and XlsxWriter from Odoo 12.0'})

        title_format = workbook.add_format({
            'bold': 1,
            'align': 'center',
            'valign': 'vcenter',
            'font_size': 14,
        })
        bg_black_format = workbook.add_format({
            'fg_color': '#000000',
            'font_color': 'white',
            'align': 'center',
            'valign': 'vcenter',
            'font_size': 14,
        })
        bg_gray_format = workbook.add_format({
            'fg_color': '#797979',
            'font_color': 'white',
            'align': 'center',
            'valign': 'vcenter',
            'font_size': 14,
        })
        border_format = workbook.add_format({
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'font_size': 14,
        })
        border_gray_format = workbook.add_format({
            'border': 1,
            'fg_color': '#afafaf',
            'align': 'center',
            'valign': 'vcenter',
            'font_size': 14,
        })
        border_grayl_format = workbook.add_format({
            'border': 1,
            'fg_color': '#d5d5d5',
            'align': 'center',
            'valign': 'vcenter',
            'font_size': 12,
        })
        font_size_format = workbook.add_format({
            'font_size': 14,
        })

        image_path = get_module_resource(
            'paperwork_usa', 'static/img', 'LogoGebesaLema.png')
        image = tools.image_resize_image_medium(base64.b64encode(
            open(image_path, 'rb').read()), size=(166, 55),)
        image = io.BytesIO(base64.b64decode(image))

        for ship in objects:
            for partner in ship.partner_ids:
                sum_pitex = 0
                sum_qty = 0
                sum_cubic = 0
                sheet = workbook.add_worksheet(_(
                    'Packing List ' + str(partner.partner_id.id)))
                sheet.set_landscape()
                sheet.fit_to_pages(1, 0)
                sheet.set_zoom(90)

                # # Title rows
                sheet.set_column(0, 0, 15)
                sheet.set_column(1, 2, 20)
                sheet.set_column(3, 3, 25)
                sheet.set_column(4, 4, 70)
                sheet.set_column(5, 5, 20)
                sheet.set_column(6, 6, 25)
                sheet.set_column(7, 7, 10)
                sheet.set_column(8, 8, 15)
                sheet.set_row(0, 8)
                sheet.set_row(1, 30)
                sheet.set_row(2, 25)
                sheet.set_row(3, 25)
                sheet.set_row(4, 8)
                sheet.set_row(5, 25)
                sheet.set_row(6, 25)
                sheet.set_row(7, 25)
                sheet.set_row(8, 5)
                sheet.set_row(12, 30)

                sheet.merge_range('A1:I1', '', bg_black_format)

                sheet.merge_range(
                    'A2:B3', '', title_format)
                sheet.insert_image('A2:B3', "image.png", {
                    'image_data': image, 'x_offset': 30, 'y_offset': 10})
                sheet.merge_range(
                    'C2:E2', 'PACKING LIST', title_format)
                sheet.merge_range(
                    'F2:G2', 'Revisión: 0', title_format)

                sheet.merge_range(
                    'C3:D3', 'Código: F-LOG-02', title_format)
                sheet.write('E3', 'Deriva de: P-LOG-01', title_format)
                sheet.merge_range(
                    'F3:G3', 'Fecha de Revisión: %s' % fields.Date.today(
                    ).strftime('%d/%m/%Y'), title_format)

                sheet.merge_range('A5:I5', '', bg_black_format)

                sheet.write('A6', '● SHIP TO:', font_size_format)
                sheet.merge_range(
                    'B6:C6', partner.partner_id.name, font_size_format)
                sheet.write('D6', '● DATE:', font_size_format)
                sheet.write('E6', fields.Date.today().strftime(
                    '%d/%m/%Y'), font_size_format)
                sheet.write('G6', '● SEAL:', font_size_format)
                sheet.merge_range('H6:I6', ship.seal, font_size_format)

                addr = (partner.partner_id.street or '') +\
                    ' ' + (partner.partner_id.street_number or '') +\
                    '\n ' + (partner.partner_id.street2 or '') +\
                    ' ' + (partner.partner_id.city or '') +\
                    '\n ' + (partner.partner_id.state_id.name or '') +\
                    ' CP ' + (str(partner.partner_id.zip) or '')
                sheet.merge_range('B7:C8', addr, font_size_format)
                sheet.write('D7', '● TRUCK:', font_size_format)
                sheet.write('E7', ship.trailer_number, font_size_format)
                sheet.write('G7', '● WEIGHT Kg:', font_size_format)

                sheet.write('D8', '● LICENSE', font_size_format)
                sheet.write('E8', ship.plaque, font_size_format)
                sheet.write('G8', '● TOTAL PACKAGES', font_size_format)

                sheet.merge_range(
                    'A10:I11',
                    "● DELIVERY INSTRUCTIONS: " + (partner.partner_id.comment or ''), font_size_format)

                sheet.merge_range('A12:I12', 'PACKING LIST', bg_black_format)

                sheet.write('A13', 'PACKAGES', bg_gray_format)
                sheet.write('B13', 'PURCHASE ORDER', bg_gray_format)
                sheet.write('C13', 'SALES ORDER', bg_gray_format)
                sheet.write('D13', 'VENDOR ITEM \nNUMBER', bg_gray_format)
                sheet.write('E13', 'DESCRIPTION', bg_gray_format)
                sheet.write('F13', 'INVOICE', bg_gray_format)
                sheet.write('G13', 'KG', bg_gray_format)
                sheet.write('H13', 'QTY', bg_gray_format)
                sheet.write('I13', 'M3', bg_gray_format)

                products = ship.with_context(
                    lang=partner.partner_id.lang).mapped(
                    'line_ids').filtered(
                    lambda l: l.partner_shipping_id.id == partner.partner_id.id)

                lang_company = self.env.user.company_id.partner_id.lang
                i = 14
                for line in products:
                    invoice = ''
                    if line.order_line_id.invoice_lines:
                        invoice = self.env['account.invoice'].search([
                            ('state', '!=', 'cancel'),
                            ('id', 'in',
                             line.order_line_id.invoice_lines.mapped(
                                 'invoice_id').ids)],
                            order='date_invoice desc', limit=1)
                        invoice = invoice.number
                    pitex = round(
                        line.product_id.weight * line.quantity_shipped, 2)
                    cubic = round(
                        line.product_id.volume * line.quantity_shipped, 2)
                    bom = self.env['mrp.bom'].with_context(
                        lang=partner.partner_id.lang).search([
                            ('product_id', '=', line.product_id.id),
                            ('active', '=', True)], limit=1)

                    if bom.type != 'phantom':
                        sheet.write('A' + str(i), '', border_format)
                        sheet.write(
                            'B' + str(i), line.sale_order_id.client_order_ref,
                            border_format)
                        sheet.write(
                            'C' + str(i), line.sale_order_id.name,
                            border_format)
                        if line.order_line_id.reference_code:
                            sheet.write(
                                'D' + str(i), line.product_id.default_code + '[' + str(line.order_line_id.reference_code) + ']', border_format)
                        else:
                            sheet.write(
                                'D' + str(i), line.product_id.default_code, border_format)
                        # sheet.write(
                            # 'D' + str(i), line.product_id.default_code,
                            # border_format)
                        sheet.write(
                            'E' + str(i), line.product_id.name, border_format)
                        sheet.write('F' + str(i), invoice, border_format)
                        sheet.write('G' + str(i), pitex, border_format)
                        sheet.write(
                            'H' + str(i), line.quantity_shipped, border_format)
                        sheet.write('I' + str(i), cubic, border_format)
                        if lang_company != partner.partner_id.lang:
                            sheet.write(
                                'J' + str(i),
                                line.product_id.with_context(
                                    lang=lang_company).product_tmpl_id.name,
                                font_size_format)
                    else:
                        pitex = 0
                        sheet.write('A' + str(i), '', border_gray_format)
                        sheet.write(
                            'B' + str(i), line.sale_order_id.client_order_ref,
                            border_gray_format)
                        sheet.write(
                            'C' + str(i), line.sale_order_id.name,
                            border_gray_format)
                        if line.order_line_id.reference_code:
                            sheet.write(
                                'D' + str(i), line.product_id.default_code + '[' + str(line.order_line_id.reference_code) + ']', border_format)
                        else:
                            sheet.write(
                                'D' + str(i), line.product_id.default_code, border_format)
                        # sheet.write(
                            # 'D' + str(i), line.product_id.default_code,
                            # border_gray_format)
                        sheet.write(
                            'E' + str(i), line.product_id.product_tmpl_id.name,
                            border_gray_format)
                        sheet.write('F' + str(i), invoice, border_gray_format)
                        sheet.write('G' + str(i), '', border_gray_format)
                        sheet.write(
                            'H' + str(i), line.quantity_shipped,
                            border_gray_format)
                        sheet.write('I' + str(i), cubic, border_gray_format)
                        if lang_company != partner.partner_id.lang:
                            sheet.write(
                                'J' + str(i),
                                line.product_id.with_context(
                                    lang=lang_company).product_tmpl_id.name,
                                font_size_format)
                        for mbl in bom.bom_line_ids:
                            i = i + 1
                            mbl_qty = round(
                                mbl.product_qty * line.quantity_shipped, 2)
                            mbl_pitex = round(
                                mbl.product_id.weight * mbl_qty, 2)
                            pitex += mbl_pitex
                            sheet.write('A' + str(i), '', border_grayl_format)
                            sheet.write(
                                'B' + str(i), '', border_grayl_format)
                            sheet.write(
                                'C' + str(i), '', border_grayl_format)
                            if line.order_line_id.reference_code:
                                sheet.write(
                                    'D' + str(i), mbl.product_id.default_code + '[' + str(line.order_line_id.reference_code) + ']', border_format)
                            else:
                                sheet.write(
                                    'D' + str(i), mbl.product_id.default_code, border_format)
                            # sheet.write(
                                # 'D' + str(i), mbl.product_id.default_code,
                                # border_grayl_format)
                            sheet.write(
                                'E' + str(i),
                                mbl.product_id.product_tmpl_id.name,
                                border_grayl_format)
                            sheet.write('F' + str(i), '', border_grayl_format)
                            sheet.write(
                                'G' + str(i), mbl_pitex, border_grayl_format)
                            sheet.write(
                                'H' + str(i), mbl_qty, border_grayl_format)
                            sheet.write(
                                'I' + str(i), '', border_grayl_format)
                            if lang_company != partner.partner_id.lang:
                                sheet.write(
                                    'J' + str(i),
                                    mbl.product_id.with_context(
                                        lang=lang_company).product_tmpl_id.name,
                                    font_size_format)

                    i = i + 1
                    sum_pitex += pitex
                    sum_qty += line.quantity_shipped
                    sum_cubic += cubic

                for j in range(3):
                    sheet.write('A' + str(i), '', border_format)
                    sheet.write('B' + str(i), '', border_format)
                    sheet.write('C' + str(i), '', border_format)
                    sheet.write('D' + str(i), '', border_format)
                    sheet.write('E' + str(i), '', border_format)
                    sheet.write('F' + str(i), '', border_format)
                    sheet.write('G' + str(i), '', border_format)
                    sheet.write('H' + str(i), '', border_format)
                    sheet.write('I' + str(i), '', border_format)
                    i += 1

                sheet.write('A' + str(i), '', bg_black_format)
                sheet.write('B' + str(i), 'TOTAL', bg_black_format)
                sheet.write('C' + str(i), '', bg_black_format)
                sheet.write('D' + str(i), '', bg_black_format)
                sheet.write('E' + str(i), '', bg_black_format)
                sheet.write('F' + str(i), 'TOTAL', bg_black_format)
                sheet.write('G' + str(i), sum_pitex, bg_black_format)
                sheet.write('H' + str(i), sum_qty, bg_black_format)
                sheet.write('I' + str(i), sum_cubic, bg_black_format)

                sheet.merge_range('H7:I7', sum_pitex, font_size_format)
                sheet.merge_range('H8:I8', sum_qty, font_size_format)
