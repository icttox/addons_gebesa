# Copyright 2021, Samuel Barron
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import logging
from odoo import models

_logger = logging.getLogger(__name__)

DATA = {
    'tipo_operacion': {
        'out_invoice': 'Exportación',
        'in_invoice': 'Importación'
    },
    'tipo_figura': {
        'out_invoice': 'Exportador',
        'in_invoice': 'Importador'
    }
}


def copy_format(book, fmt):
    properties = [f[4:] for f in dir(fmt) if f[0:4] == 'set_']
    dft_fmt = book.add_format()
    res = book.add_format(
        {k: v for k, v in fmt.__dict__.items() if k in properties and dft_fmt.__dict__[k] != v})
    return res


class ExportSiimmexInvoiceXlsx(models.AbstractModel):
    _name = 'report.immex_gebesa.export_siimex_invoice_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, objects):
        usd = self.env.ref('base.USD')
        workbook.set_properties({
            'comments': 'Created with Python and XlsxWriter from Odoo 12.0'})
        bold = workbook.add_format({'bold': True})

        sheet = workbook.add_worksheet(
            'Hoja1')
        sheet.set_landscape()
        sheet.fit_to_pages(1, 0)
        sheet.set_zoom(90)

        sheet.write('A1', 'factura', bold)
        sheet.write('B1', 'tipo_operacion', bold)
        sheet.write('C1', 'tipo_figura', bold)
        sheet.write('D1', 'fecha_expedicion', bold)
        sheet.write('E1', 'rfc_consulta', bold)
        sheet.write('F1', 'patente_aduanal', bold)
        sheet.write('G1', 'sub_division', bold)
        sheet.write('H1', 'certificado_origen', bold)
        sheet.write('I1', 'tipo_identificador_proveedor', bold)
        sheet.write('J1', 'Tax ID/Sin Tax ID/RFC/CURP', bold)
        sheet.write('K1', 'Proveedor_razon_social', bold)
        sheet.write('L1', 'tipo_identificador_destinatario', bold)
        sheet.write('M1', 'Tax ID/Sin Tax ID/RFC/CURP', bold)
        sheet.write('N1', 'Destinatario_razon_social', bold)
        sheet.write('O1', 'relacion_facturas', bold)
        sheet.write('P1', 'observaciones', bold)
        sheet.write('Q1', 'descripcion_mercancia', bold)
        sheet.write('R1', 'clave_unidad_medida', bold)
        sheet.write('S1', 'cantidad', bold)
        sheet.write('T1', 'tipo_moneda', bold)
        sheet.write('U1', 'precio_unitario', bold)
        sheet.write('V1', 'valot_total', bold)
        sheet.write('W1', 'valor_total_usd', bold)
        sheet.write('X1', 'marca', bold)
        sheet.write('Y1', 'serie', bold)
        sheet.write('Z1', 'modelo', bold)
        sheet.write('AA1', 'submodelo', bold)
        rownum = 2
        for invoice in objects:
            proveedor = invoice.partner_id
            destinatario = invoice.company_id.partner_id
            identificador_p = 'RFC'
            identificador_d = 'TAX_ID'
            if invoice.type == 'out_invoice':
                proveedor = invoice.company_id.partner_id
                destinatario = invoice.partner_id
                identificador_p = 'TAX_ID'
                identificador_d = 'RFC'
            sheet.write('A' + str(rownum), invoice.number)
            sheet.write('B' + str(rownum), DATA['tipo_operacion'][invoice.type])
            sheet.write('C' + str(rownum), DATA['tipo_figura'][invoice.type])
            sheet.write('D' + str(rownum), invoice.date_invoice.strftime('%d/%m/%Y'))
            sheet.write('E' + str(rownum), invoice.company_id.partner_id.vat)
            sheet.write('F' + str(rownum), '')
            sheet.write('G' + str(rownum), '0')
            sheet.write('H' + str(rownum), '1')
            sheet.write('I' + str(rownum), identificador_p)
            sheet.write('J' + str(rownum), proveedor.vat)
            sheet.write('K' + str(rownum), proveedor.name)
            sheet.write('L' + str(rownum), identificador_d)
            sheet.write('M' + str(rownum), destinatario.vat)
            sheet.write('N' + str(rownum), destinatario.name)
            sheet.write('O' + str(rownum), '0')
            sheet.write('P' + str(rownum), 'NA')
            rownum += 1
            for line in invoice.invoice_line_ids:
                sheet.write('Q' + str(rownum), line.name)
                sheet.write('R' + str(rownum), line.uom_id.fiscal_code)
                sheet.write('S' + str(rownum), line.quantity)
                sheet.write('T' + str(rownum), invoice.currency_id.name)
                sheet.write('U' + str(rownum), line.price_unit)
                sheet.write('V' + str(rownum), line.price_total)
                total_usd = line.price_total
                if usd.id != invoice.currency_id.id:
                    total_usd = invoice.currency_id._convert(
                        total_usd, usd,
                        invoice.company_id, invoice.date_invoice)
                sheet.write('W' + str(rownum), total_usd)
                rownum += 1
