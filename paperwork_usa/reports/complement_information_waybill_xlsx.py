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


class ComplementInformationWaybillXlsx(models.AbstractModel):
    _name = 'report.paperwork_usa.complement_information_waybill_xlsx'
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
                sudo_res_partner = self.env['res.partner'].sudo().browse(partner.partner_id.id)
                sum_pitex = 0
                sum_qty = 0
                sheet = workbook.add_worksheet(_(
                    'ubicacion ' + str(sudo_res_partner.id)))
                sheet.set_landscape()
                sheet.fit_to_pages(1, 0)
                sheet.set_zoom(80)

                # Title rows
                sheet.set_column(0, 0, 25)
                sheet.set_column(1, 1, 60)
                sheet.set_column(2, 2, 30)
                sheet.set_column(3, 3, 15)
                sheet.set_column(4, 11, 25)
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

                sheet.merge_range('A1:L1', '', bg_black_format)

                sheet.merge_range(
                    'A2:B3', '', title_format)
                sheet.insert_image('A2:B3', "image.png", {
                    'image_data': image, 'x_offset': 30, 'y_offset': 10})
                sheet.merge_range(
                    'C2:G2', 'Informacion de complemento Carta Porte', title_format)
                # sheet.merge_range(
                #     'F2:G2', 'Revisión: 0', title_format)

                # sheet.merge_range(
                #     'C3:D3', 'Código: F-LOG-02', title_format)
                # sheet.write('E3', 'Deriva de: P-LOG-01', title_format)
                # sheet.merge_range(
                #     'F3:G3', 'Fecha de Revisión: %s' % fields.Date.today(
                #     ).strftime('%d/%m/%Y'), title_format)

                sheet.merge_range('A5:L5', '', bg_black_format)

                sheet.write('A6', '● ENVIAR A:', font_size_format)
                sheet.merge_range(
                    'B6:C6', sudo_res_partner.name, font_size_format)
                sheet.write('D6', '● FECHA:', font_size_format)
                sheet.write('E6', fields.Date.today().strftime(
                    '%d/%m/%Y'), font_size_format)
                sheet.write('G6', '● MONEDA:', font_size_format)
                sheet.merge_range(
                    'H6:I6',
                    sudo_res_partner.property_product_pricelist.currency_id.name,
                    font_size_format)

                addr = (sudo_res_partner.street or '') +\
                    ' ' + (sudo_res_partner.street_number or '') +\
                    '\n ' + (sudo_res_partner.street2 or '') +\
                    ' ' + (sudo_res_partner.city or '') +\
                    '\n ' + (sudo_res_partner.state_id.name or '') +\
                    ' CP ' + (str(sudo_res_partner.zip) or '')
                sheet.merge_range('B7:C8', addr, font_size_format)
                # sheet.write('D7', '● TRUCK:', font_size_format)
                # sheet.write('E7', ship.trailer_number, font_size_format)
                sheet.write('G7', '● PESO Kg:', font_size_format)

                # sheet.write('D8', '● LICENSE', font_size_format)
                # sheet.write('E8', ship.plaque, font_size_format)
                sheet.write('G8', '● PAQUETES TOTALES:', font_size_format)

                sheet.merge_range(
                    'A10:I11',
                    "● INSTRUCCIONES DE ENTREGA: " + (sudo_res_partner.comment or ''), font_size_format)

                sheet.merge_range('A12:K12', 'PRODUCTOS', bg_black_format)

                sheet.write('A13', 'Clave del Producto', bg_gray_format)
                sheet.write('B13', 'Nombre del producto', bg_gray_format)
                sheet.write('C13', 'Clave del producto o \nservicio del producto', bg_gray_format)
                sheet.write('D13', 'Cantidad', bg_gray_format)
                sheet.write('E13', 'Precio Unitario', bg_gray_format)
                sheet.write('F13', 'Peso bruto (KG)', bg_gray_format)
                sheet.write('G13', 'Clave fiscal de la \nunidad de medida del producto', bg_gray_format)
                sheet.write('H13', 'Nombre de la unidad \nde medida', bg_gray_format)
                sheet.write('I13', 'Fracción arancelaria \ndel producto', bg_gray_format)
                sheet.write('J13', 'UUID de la Factura', bg_gray_format)
                sheet.write('K13', 'Exportacion', bg_gray_format)
                sheet.write('L13', 'Dimensiones', bg_gray_format)

                lang_company = self.env.user.company_id.partner_id.lang
                products = ship.with_context(
                    lang=sudo_res_partner.lang).mapped(
                    'line_ids').filtered(
                    lambda l: l.partner_shipping_id.id == sudo_res_partner.id)
                i = 14
                for line in products:
                    invoice = ''
                    sudo_sol = self.env['sale.order.line'].sudo().browse(line.order_line_id.id)
                    sudo_product = self.env['product.product'].sudo().browse(line.product_id.id)
                    inv_line = self.env['account.invoice.line']
                    if sudo_sol.invoice_lines:
                        invoice = self.env['account.invoice'].search([
                            ('state', '!=', 'cancel'),
                            ('id', 'in',
                             sudo_sol.invoice_lines.mapped(
                                 'invoice_id').ids)],
                            order='date_invoice desc', limit=1)
                        inv_line = sudo_sol.invoice_lines.filtered(
                            lambda lin: lin.invoice_id.id == invoice.id)
                        invoice = invoice.l10n_mx_edi_cfdi_uuid
                    pitex = round(
                        sudo_product.weight * line.quantity_shipped, 2)
                    bom = self.env['mrp.bom'].with_context(
                        lang=sudo_res_partner.lang).search([
                            ('product_id', '=', sudo_product.id),
                            ('active', '=', True)], limit=1)

                    if bom.type != 'phantom':
                        sheet.write(
                            'A' + str(i), sudo_product.default_code,
                            border_format)
                        sheet.write(
                            'B' + str(i), sudo_product.product_tmpl_id.name,
                            border_format)
                        sheet.write(
                            'C' + str(i),
                            sudo_product.l10n_mx_edi_code_sat_id.code or '',
                            border_format)
                        sheet.write('D' + str(i), line.quantity_shipped, border_format)
                        sheet.write('E' + str(i), round(inv_line.price_unit, 2), border_format)
                        sheet.write('F' + str(i), pitex, border_format)
                        sheet.write(
                            'G' + str(i),
                            sudo_sol.product_uom.l10n_mx_edi_code_sat_id.code,
                            border_format)
                        sheet.write(
                            'H' + str(i), sudo_sol.product_uom.name,
                            border_format)
                        sheet.write(
                            'I' + str(i),
                            sudo_product.l10n_mx_edi_tariff_fraction_id.code or '',
                            border_format)
                        sheet.write(
                            'J' + str(i), invoice or '',
                            border_format)
                        # sheet.write('J' + str(i), invoice., border_format)
                        sheet.write('K' + str(i), '', border_format)
                        sheet.write('L' + str(i), '', border_format)
                        if lang_company != sudo_res_partner.lang:
                            sheet.write(
                                'M' + str(i),
                                sudo_product.with_context(
                                    lang=lang_company).product_tmpl_id.name,
                                font_size_format)
                    else:
                        pitex = 0

                        sheet.write(
                            'A' + str(i), sudo_product.default_code,
                            border_gray_format)
                        sheet.write(
                            'B' + str(i), sudo_product.product_tmpl_id.name,
                            border_gray_format)
                        sheet.write(
                            'C' + str(i),
                            sudo_product.l10n_mx_edi_code_sat_id.code or '',
                            border_gray_format)
                        sheet.write(
                            'D' + str(i), line.quantity_shipped,
                            border_gray_format)
                        sheet.write('E' + str(i), round(inv_line.price_unit, 2), border_gray_format)
                        sheet.write(
                            'G' + str(i),
                            sudo_sol.product_uom.l10n_mx_edi_code_sat_id.code,
                            border_gray_format)
                        sheet.write(
                            'H' + str(i), sudo_sol.product_uom.name,
                            border_gray_format)
                        sheet.write(
                            'I' + str(i),
                            sudo_product.l10n_mx_edi_tariff_fraction_id.code or '',
                            border_gray_format)
                        sheet.write(
                            'J' + str(i), invoice or '',
                            border_gray_format)
                        sheet.write('K' + str(i), '', border_gray_format)
                        sheet.write('L' + str(i), '', border_gray_format)
                        if lang_company != sudo_res_partner.lang:
                            sheet.write(
                                'M' + str(i),
                                sudo_product.with_context(
                                    lang=lang_company).product_tmpl_id.name,
                                font_size_format)
                        i_enc = i
                        for mbl in bom.bom_line_ids:
                            i = i + 1
                            mbl_qty = round(
                                mbl.product_qty * line.quantity_shipped, 2)
                            mbl_pitex = round(
                                mbl.product_id.weight * mbl_qty, 2)
                            pitex += mbl_pitex
                            sheet.write(
                                'A' + str(i), mbl.product_id.default_code,
                                border_grayl_format)
                            sheet.write(
                                'B' + str(i),
                                mbl.product_id.product_tmpl_id.name,
                                border_grayl_format)
                            sheet.write(
                                'C' + str(i),
                                mbl.product_id.l10n_mx_edi_code_sat_id.code or '',
                                border_grayl_format)
                            sheet.write(
                                'D' + str(i), mbl_qty,
                                border_grayl_format)
                            sheet.write(
                                'E' + str(i), '',
                                border_grayl_format)
                            sheet.write(
                                'F' + str(i),
                                mbl_pitex,
                                border_grayl_format)
                            sheet.write(
                                'G' + str(i),
                                mbl.product_uom_id.l10n_mx_edi_code_sat_id.code,
                                border_grayl_format)
                            sheet.write(
                                'H' + str(i), mbl.product_uom_id.name,
                                border_grayl_format)
                            sheet.write(
                                'I' + str(i),
                                mbl.product_id.l10n_mx_edi_tariff_fraction_id.code or '',
                                border_grayl_format)
                            sheet.write(
                                'J' + str(i), invoice or '',
                                border_grayl_format)
                            sheet.write('K' + str(i), '', border_grayl_format)
                            sheet.write('L' + str(i), '', border_grayl_format)
                            if lang_company != sudo_res_partner.lang:
                                sheet.write(
                                    'M' + str(i),
                                    mbl.product_id.with_context(
                                        lang=lang_company).product_tmpl_id.name,
                                    font_size_format)
                        sheet.write(
                            'F' + str(i_enc), pitex,
                            border_gray_format)

                    i = i + 1
                    sum_pitex += pitex
                    sum_qty += line.quantity_shipped

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
                    sheet.write('J' + str(i), '', border_format)
                    sheet.write('K' + str(i), '', border_format)
                    sheet.write('L' + str(i), '', border_format)
                    i += 1

                sheet.write('A' + str(i), '', bg_black_format)
                sheet.write('B' + str(i), 'TOTAL', bg_black_format)
                sheet.write('C' + str(i), '', bg_black_format)
                sheet.write('D' + str(i), sum_qty, bg_black_format)
                sheet.write('E' + str(i), sum_pitex, bg_black_format)
                sheet.write('F' + str(i), '', bg_black_format)
                sheet.write('G' + str(i), '', bg_black_format)
                sheet.write('H' + str(i), '', bg_black_format)
                sheet.write('I' + str(i), '', bg_black_format)
                sheet.write('J' + str(i), '', bg_black_format)
                sheet.write('K' + str(i), '', bg_black_format)
                sheet.write('L' + str(i), '', bg_black_format)

                sheet.merge_range('H7:I7', sum_pitex, font_size_format)
                sheet.merge_range('H8:I8', sum_qty, font_size_format)
