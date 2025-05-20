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

class TmecFormatXlsx(models.AbstractModel):
    _name = 'report.paperwork_usa.tmec_format_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, objects):
        workbook.set_properties({
            'comments': 'Created with Python and XlsxWriter from Odoo 12.0'})
        consecutive = 1
        for ship in objects:
            for partner in ship.partner_ids:
                sheet = workbook.add_worksheet(_('TMEC Format ' + str(
                    consecutive) + ' ' + partner.partner_id.name))
                consecutive = consecutive + 1
                sheet.set_landscape()
                sheet.fit_to_pages(1, 0)
                sheet.set_zoom(90)

                # bold = workbook.add_format({'bold': True})
                # Title rows
                # sheet.set_column('A:M', 12)
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
                formatwrap.set_bold()
                formatwrap.set_border(style=1)
                formatwrap.set_align('top')
                # Mezclar rango de A a M
                sheet.merge_range('A1:C1', 'CERTIFICACION DE ORIGEN', merge_format)

                new_format = copy_format(workbook, merge_format)
                new_format.set_align('left')
                new_format.set_text_wrap()
                new_format.set_border(style=1)

                onlyborder = workbook.add_format()
                onlyborder.set_border(style=1)

                # First section section
                sheet.set_row(2, 50)
                sheet.set_column('A:A', 72)
                text = '1.- Priodo Global (dd/mm/aa) \n' +\
                    'De: 01/07/20        A: 31/12/20'
                sheet.write('A3', text, formatwrap)

                facturas = ship._get_invoices()
                sheet.set_column('B:C', 36)
                text = '2.- Envío individual \n' +\
                    'Número de factura: ' + facturas
                sheet.merge_range('B3:C3', text, formatwrap)
                #sheet.write('B1', text, formatwrap)

                # Second section
                addr = (self.env.user.company_id.street or '') +\
                    ' ' + (self.env.user.company_id.street_number or '') +\
                    ' ' + (self.env.user.company_id.street2 or '') +\
                    ' ' + (self.env.user.company_id.city or '') +\
                    ' ' + (self.env.user.company_id.state_id.name or '') +\
                    ' CP ' + (str(self.env.user.company_id.zip) or '')

                sheet.set_row(3, 210)
                text = '3.- Certificador \n' +\
                    'Nombre: ' + self.env.user.company_id.name + '\n' +\
                    self.env.user.partner_id.name + '\n' +\
                    'Cargo: Departamento de Exportación \n\n' +\
                    'Dirección: ' + addr + '\n\n' +\
                    'No. Teléfono: ' + self.env.user.company_id.phone + '\n\n' +\
                    'Dirección de Correo electrónico: ' + self.env.user.login + '\n\n' +\
                    'Parte Certificadora:    ☑ Exportador      □ Importador      □ Productor'
                sheet.write('A4', text, formatwrap)

                text = '4.- Exportador (de ser distinto del certificador) \n\n\n' +\
                    'Nombre: \n\n' +\
                    'Dirección: \n\n\n' +\
                    'No. Teléfono: \n\n' +\
                    'Dirección de Correo electrónico: \n\n'
                sheet.merge_range('B4:C4', text, formatwrap)

                # Third section section
                partaddr = (partner.partner_id.street_number or '') +\
                    ' ' + (partner.partner_id.street or '') +\
                    ' ' + (partner.partner_id.street2 or '') +\
                    ' ' + (partner.partner_id.city or '') +\
                    ' ' + (partner.partner_id.state_id.name or '') +\
                    ' ' + (str(partner.partner_id.zip) or '')

                sheet.set_row(4, 170)
                text = '5.- Productor (de ser distinto del certificador) \n' +\
                    'Nombre: \n\n' +\
                    'Dirección:                                         Varios: ▭\n\n' +\
                    'No. Teléfono: \n\n' +\
                    'Dirección de Correo electrónico: \n\n'
                sheet.write('A5', text, formatwrap)

                text = '6.- Importador (de conocerse) \n' +\
                    'Nombre: ' + partner.partner_id.name + '\n\n' +\
                    'Dirección: ' + partaddr + '\n\n' +\
                    'No. Teléfono: ' + str(partner.partner_id.phone) + '\n\n' +\
                    'Dirección de Correo electrónico: ' + str(partner.partner_id.email) + '\n\n'
                sheet.merge_range('B5:C5', text, formatwrap)

                sheet.set_row(5, 50)
                sheet.write('A6', '7.- Descripción de la mercancía', formatwrap)
                sheet.write(
                    'B6',
                    '8.- Clasificación Arancelaria de la mercancía en el Sistema '
                    'Armonizado (a seis digitos)',
                    formatwrap)
                sheet.write('C6', '9.- Criterio de origen', formatwrap)

                products = self.env['mrp.shipment.line'].search([
                    ('shipment_id', '=', ship.id),
                    ('partner_shipping_id', '=', partner.partner_id.id),
                    (
                        'product_id.line_id',
                        'not in',
                        self.env.user.company_id.foreign_line_ids.ids)])

                i = 7
                for line in products:
                    # sheet.set_row(i, 35)
                    sheet.write(
                        'A' + str(i),
                        '[' + line.product_id.default_code + '] ' +
                        line.product_id.name or '',
                        onlyborder)

                    fraccion = (
                        line.product_id.l10n_mx_edi_tariff_fraction_id.code[:6]
                    ) if line.product_id.l10n_mx_edi_tariff_fraction_id else 'No tiene'
                    sheet.write(
                        'B' + str(i),
                        fraccion,
                        onlyborder)

                    sheet.write('C' + str(i), 'B', onlyborder)
                    i += 1

                sheet.set_row(i - 1, 90)
                rangmerg = 'A' + str(i) + ':C' + str(i)
                sheet.merge_range(
                    rangmerg,
                    '10- Certifico que las mercancías descritas en este documento '
                    'califican como originarias y que la información contenida en '
                    'este documento es verdadera y exacta. Asumo la responsabilidad '
                    'de comprobar lo aquí declarado y me comprometo a conservar y '
                    'presentar en caso de ser requerido o a poner a disposición '
                    'durante una visita de verificación, la documentación necesaria '
                    'que soporte esta certificación. \n\n '
                    'Este certificado se compone de ___ hojas, incluyendo todos sus '
                    'anexos.',
                    formatwrap)
                i += 1

                sheet.set_row(i - 1, 70)
                sheet.write('A' + str(i), 'Firma autorizada del Certificador', formatwrap)

                rangmerg = 'B' + str(i) + ':C' + str(i)
                fecha = 'Fecha de la certificación: \n\n D D / M M / A A \n' +\
                    fields.Date.today().strftime('%d/%m/%y')
                sheet.merge_range(
                    rangmerg,
                    fecha,
                    formatwrap)
