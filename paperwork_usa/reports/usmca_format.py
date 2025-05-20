# Copyright 2020, Cesar Barron
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import logging
from odoo import fields, models
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)

def copy_format(book, fmt):
    properties = [f[4:] for f in dir(fmt) if f[0:4] == 'set_']
    dft_fmt = book.add_format()
    res = book.add_format(
        {k: v for k, v in fmt.__dict__.items() if k in properties and dft_fmt.__dict__[k] != v})
    return res

class UsmcaFormatXlsx(models.AbstractModel):
    _name = 'report.paperwork_usa.usmca_format_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, objects):
        workbook.set_properties({
            'comments': 'Created with Python and XlsxWriter from Odoo 12.0'})
        consecutive = 1
        for ship in objects:
            for partner in ship.partner_ids:
                sheet = workbook.add_worksheet(_('USMCA Format ' + str(
                    consecutive) + ' ' + partner.partner_id.name))
                consecutive = consecutive + 1
                sheet.set_landscape()
                sheet.fit_to_pages(1, 0)
                sheet.set_zoom(90)

                bold = workbook.add_format({'bold': True})
                # Title rows
                sheet.set_column('A:M', 12)
                sheet.set_row(0, 30)
                # Crear el formato para las celdas mezcladas
                merge_format = workbook.add_format({
                    'bold': 1,
                    'border': 1,
                    'align': 'center',
                    'valign': 'vcenter',
                    'fg_color': 'silver'})

                formatwrap = workbook.add_format()
                formatwrap.set_text_wrap()
                formatwrap.set_align('top')
                # Mezclar rango de A a M
                sheet.merge_range('A1:M1', 'USMCA CERTIFICATE ORIGIN', merge_format)

                new_format = copy_format(workbook, merge_format)

                # First header section
                sheet.set_column('A:G', 12)
                sheet.set_row(2, 30)
                new_format.set_align('left')
                new_format.set_text_wrap()
                # Mezclar rango de A a G
                sheet.merge_range('A3:G3', '1.- EXPORTER INFORMATION', new_format)
                # Mezclar rango de H a M
                # sheet.set_column('H:M', 12)
                sheet.merge_range('H3:M3', '2.- BLANKET PERIOD', new_format)

                new_format.set_bold(0)
                sheet.merge_range('A4:A5', 'NAME', new_format)
                sheet.merge_range('C4:G5', self.env.user.company_id.name, formatwrap)

                sheet.merge_range('I4:M4', 'MM/DD/YYYY')
                sheet.write('I5', 'FROM', bold)
                sheet.write('J5', '07/01/20')

                addr = (self.env.user.company_id.street or '') +\
                    ' ' + (self.env.user.company_id.street_number or '') +\
                    ' ' + (self.env.user.company_id.street2 or '') +\
                    ' ' + (self.env.user.company_id.city or '') +\
                    ' ' + (self.env.user.company_id.state_id.name or '') +\
                    ' CP ' + (str(self.env.user.company_id.zip) or '')

                sheet.merge_range('A6:A7', 'ADDRESS', new_format)
                sheet.merge_range('C6:G7', addr, formatwrap)
                sheet.write('I6', 'TO', bold)
                sheet.write('J6', '12/31/20')

                sheet.write('A8', 'Email', bold)
                sheet.write('C8', self.env.user.login)

                sheet.write('A9', 'Telephone', bold)
                sheet.write('C9', self.env.user.company_id.phone)

                sheet.write('A10', 'TAX ID', bold)
                sheet.write('C10', self.env.user.company_id.vat)

                sheet.merge_range('H7:M10', '')

                sheet.merge_range('A11:G11', '3.- PRODUCER INFORMATION', new_format)
                sheet.merge_range('H11:M11', '4.- IMPORTER INFORMATION', new_format)

                sheet.merge_range('A12:A13', 'NAME', new_format)
                sheet.merge_range('C12:G13', self.env.user.company_id.name, formatwrap)

                sheet.merge_range('H12:H13', 'NAME', new_format)
                sheet.merge_range('I12:M13', partner.partner_id.name, formatwrap)

                sheet.merge_range('A14:A15', 'ADDRESS', new_format)
                sheet.merge_range('C14:G15', addr, formatwrap)

                partaddr = (partner.partner_id.street_number or '') +\
                    ' ' + (partner.partner_id.street or '') +\
                    ' ' + (partner.partner_id.street2 or '') +\
                    ' ' + (partner.partner_id.city or '') +\
                    ' ' + (partner.partner_id.state_id.name or '') +\
                    ' ' + (str(partner.partner_id.zip) or '')

                sheet.merge_range('H14:H15', 'ADDRESS', new_format)
                sheet.merge_range('I14:M15', partaddr, formatwrap)

                sheet.write('A16', 'Email', bold)
                sheet.write('C16', self.env.user.login)

                sheet.write('A17', 'Telephone', bold)
                sheet.write('C17', self.env.user.company_id.phone)

                sheet.write('A18', 'TAX ID', bold)
                sheet.write('C18', self.env.user.company_id.vat)

                sheet.write('H16', 'Email', bold)
                sheet.write('J16', partner.partner_id.email)

                sheet.write('H17', 'Telephone', bold)
                sheet.write('J17', partner.partner_id.phone)

                sheet.write('H18', 'TAX ID', bold)
                sheet.write('J18', partner.partner_id.vat)

                formatborder = workbook.add_format()
                formatborder.set_border(style=1)
                sheet.merge_range('A19:M19', '5.- CERTIFICATION TYPE: (Check one)', new_format)
                sheet.write('B20', 'X', formatborder)
                sheet.merge_range('C20:E20', 'EXPORTER')
                sheet.write('F20', ' ', formatborder)
                sheet.merge_range('G20:I20', 'PRODUCER')
                sheet.write('J20', ' ', formatborder)
                sheet.merge_range('K20:M20', 'IMPORTER')

                sheet.set_row(20, 30)
                sheet.merge_range('A21:D21', '6.- Item Identifier and Description', new_format)
                sheet.merge_range(
                    'E21:G21',
                    '7.- HS Tariff Classification Number (six digits)',
                    new_format)
                sheet.merge_range('H21:I21', '8.- Origin Criterion', new_format)
                sheet.merge_range('J21:K21', '9.- Qualification Method', new_format)
                sheet.merge_range('L21:M21', '10.- Country of Origin', new_format)

                products = self.env['mrp.shipment.line'].with_context(lang=partner.partner_id.lang).search([
                    ('shipment_id', '=', ship.id),
                    ('partner_shipping_id', '=', partner.partner_id.id),
                    (
                        'product_id.line_id',
                        'not in',
                        self.env.user.company_id.foreign_line_ids.ids)])

                i = 22
                for line in products:
                    # sheet.set_row(i, 35)
                    rangmerg = 'A' + str(i) + ':D' + str(i)
                    sheet.merge_range(
                        rangmerg,
                        '[' + line.product_id.default_code + '] ' +
                        line.product_id.product_tmpl_id.name or '')
                    rangmerg = 'E' + str(i) + ':G' + str(i)
                    fraccion = (
                        line.product_id.l10n_mx_edi_tariff_fraction_id.code[:4] +
                        '.' +
                        line.product_id.l10n_mx_edi_tariff_fraction_id.code[5:7]) if line.product_id.l10n_mx_edi_tariff_fraction_id else 'No tiene'
                    sheet.merge_range(
                        rangmerg,
                        fraccion)
                    rangmerg = 'H' + str(i) + ':I' + str(i)
                    sheet.merge_range(rangmerg, 'B')
                    rangmerg = 'J' + str(i) + ':K' + str(i)
                    sheet.merge_range(rangmerg, 'TS')
                    rangmerg = 'L' + str(i) + ':M' + str(i)
                    sheet.merge_range(rangmerg, 'MX')
                    i += 1

                sheet.set_row(i - 1, 60)
                rangmerg = 'A' + str(i) + ':M' + str(i)
                sheet.merge_range(
                    rangmerg,
                    'The undersigned certifies that the'
                    ' goods described in this document qualify as originating and the'
                    ' information contained in this document is true and accurate. I'
                    ' assume responsibility for proving such representations and agree'
                    ' to maintain and present upon request or to make available during'
                    ' a verification visit, documentation necessary to support this'
                    ' certification. I also agree to notify any party provided with this'
                    ' certificate of any changes that might adversely impact a certification'
                    ' previously given.',
                    formatwrap)
                i += 1
                rangmerg = 'A' + str(i) + ':G' + str(i)
                sheet.merge_range(
                    rangmerg,
                    '11.- Authorized Certifier\'s Signature: ',
                    new_format)

                rangmerg = 'H' + str(i) + ':M' + str(i)
                sheet.merge_range(
                    rangmerg,
                    '12.- Certifying Company Name & Address (including country):',
                    new_format)
                i += 1

                rangmerg = 'A' + str(i) + ':G' + str(i + 1)
                sheet.merge_range(
                    rangmerg,
                    '',
                    formatwrap)

                rangmerg = 'H' + str(i) + ':M' + str(i + 1)
                sheet.merge_range(
                    rangmerg,
                    self.env.user.company_id.name + ' ' + addr + ', México',
                    formatwrap)

                i += 2
                rangmerg = 'A' + str(i) + ':G' + str(i)
                sheet.merge_range(
                    rangmerg,
                    '13.- Authorized Certifier\'s Name: ',
                    new_format)
                rangmerg = 'H' + str(i) + ':M' + str(i)
                sheet.merge_range(
                    rangmerg,
                    '14.- Authorized Certifier\'s Title: ',
                    new_format)

                i += 1
                rangmerg = 'A' + str(i) + ':G' + str(i + 1)
                sheet.merge_range(
                    rangmerg,
                    self.env.user.partner_id.name,
                    formatwrap)
                rangmerg = 'H' + str(i) + ':M' + str(i + 1)
                sheet.merge_range(
                    rangmerg,
                    'EXPORTS',
                    formatwrap)

                i += 2
                rangmerg = 'A' + str(i) + ':C' + str(i)
                sheet.merge_range(
                    rangmerg,
                    '15.- Date (MM/DD/YYYY): ',
                    new_format)
                rangmerg = 'D' + str(i) + ':G' + str(i)
                sheet.merge_range(
                    rangmerg,
                    '16.- Telephone: ',
                    new_format)
                rangmerg = 'H' + str(i) + ':M' + str(i)
                sheet.merge_range(
                    rangmerg,
                    '17.- Email: ',
                    new_format)

                i += 1
                rangmerg = 'A' + str(i) + ':C' + str(i)
                sheet.merge_range(
                    rangmerg,
                    fields.Date.today().strftime('%d/%m/%Y'))
                rangmerg = 'D' + str(i) + ':G' + str(i)
                sheet.merge_range(
                    rangmerg,
                    self.env.user.company_id.phone)
                rangmerg = 'H' + str(i) + ':M' + str(i)
                sheet.merge_range(
                    rangmerg,
                    self.env.user.login)
