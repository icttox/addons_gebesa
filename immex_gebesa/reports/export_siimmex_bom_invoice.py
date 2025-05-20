# Copyright 2021, Samuel Barron
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import logging
from odoo import models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class BaseExportSiimmexBomXlsx(models.AbstractModel):
    _name = 'abstract.export.siimmex.bom.xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def create_sheet_bom(self, workbook, bold):
        sheet_bom = workbook.add_worksheet(
            'Lista de Materiales')
        sheet_bom.set_landscape()
        sheet_bom.fit_to_pages(1, 0)
        sheet_bom.set_zoom(90)
        sheet_bom.write('A1', 'MATERIAL PADRE', bold)
        sheet_bom.write('B1', 'NOMBRE ESTRUCTURA', bold)
        sheet_bom.write('C1', 'FECHA INICIAL', bold)
        sheet_bom.write('D1', 'MATERIAL HIJO', bold)
        sheet_bom.write('E1', 'CANTIDAD UTILIZADA', bold)
        sheet_bom.write('F1', 'PORCENTAJE MERMA', bold)
        sheet_bom.write('G1', 'PORCENTAJE DESPERDICIO', bold)

        return sheet_bom

    def insert_line_sheet_bom(self, sheet, row, parent_pp, child_pp, qty, date):
        sheet.write('A' + str(row), parent_pp.default_code)
        sheet.write('B' + str(row), parent_pp.default_code)
        sheet.write('C' + str(row), date)
        sheet.write('D' + str(row), child_pp.default_code)
        sheet.write('E' + str(row), qty)
        sheet.write('F' + str(row), 0)
        sheet.write('G' + str(row), 0)

    def create_sheet_product(self, workbook, bold):
        sheet_product = workbook.add_worksheet(
            'Productos')
        sheet_product.set_landscape()
        sheet_product.fit_to_pages(1, 0)
        sheet_product.set_zoom(90)
        sheet_product.write('A1', 'CLAVE', bold)
        sheet_product.write('B1', 'DESCRIPCION', bold)
        sheet_product.write('C1', 'DESCRIPCION INGLES', bold)
        sheet_product.write('D1', 'COMPRADO', bold)
        sheet_product.write('E1', 'VENDIDO', bold)
        sheet_product.write('F1', 'PADRE', bold)
        sheet_product.write('G1', 'HIJO', bold)
        sheet_product.write('H1', 'CATEGORIA IMPORTACION', bold)
        sheet_product.write('I1', 'FRACCION TIGIE', bold)
        sheet_product.write('J1', 'NICO', bold)
        sheet_product.write('K1', 'TIPO', bold)
        sheet_product.write('L1', 'UM BASE', bold)
        sheet_product.write('M1', 'UM COMERCIAL', bold)
        sheet_product.write('N1', 'UM FACTOR CONVERSION COMERCIAL', bold)
        sheet_product.write('O1', 'UM TARIFA', bold)
        sheet_product.write('P1', 'UM FACTOR CONVERSION TARIFA', bold)

        return sheet_product

    def insert_line_sheet_product(self, sheet, row, product):
        sheet.write(
            'A' + str(row), product.default_code)
        sheet.write(
            'B' + str(row), product.product_tmpl_id.name)
        sheet.write('C' + str(row), '')
        sheet.write('D' + str(row), 'NO')
        sheet.write('E' + str(row), 'SI')
        sheet.write('F' + str(row), 'SI')
        sheet.write('G' + str(row), 'SI')
        sheet.write('H' + str(row), '')
        if product.l10n_mx_edi_tariff_fraction_id:
            sheet.write(
                'I' + str(row),
                product.l10n_mx_edi_tariff_fraction_id.code)
        else:
            sheet.write(
                'I' + str(row), '9403900199')
        sheet.write('J' + str(row), '')
        sheet.write('K' + str(row), '')
        if product.l10n_mx_edi_umt_aduana_id:
            sheet.write(
                'L' + str(row),
                product.l10n_mx_edi_umt_aduana_id.fiscal_code)
        else:
            sheet.write(
                'L' + str(row),
                product.uom_id.fiscal_code)
        sheet.write('M' + str(row), '')
        sheet.write('N' + str(row), '')
        sheet.write('O' + str(row), '')
        sheet.write('P' + str(row), '')

    def get_data_export(self, product_ids):
        if len(product_ids) == 1:
            product_ids.append(0)
        self._cr.execute("""
            WITH RECURSIVE bom_detail(path_id,path,pt_id,pt_product,id,product,immex,location_id,qty) AS(
                SELECT
                    CAST(pp.id AS TEXT),
                    pp.default_code,
                    pp.id,
                    pp.default_code,
                    pp.id,
                    pp.default_code,
                    imm.name,
                    0,
                    1.000000
                FROM product_product AS pp
                JOIN product_template AS pt ON pt.id = pp.product_tmpl_id
                LEFT JOIN l10n_mx_immex_partida_type AS imm ON imm.id = pt.immex_type_id
                WHERE pp.salida_a24 AND pp.id IN %s
                UNION SELECT
                    CONCAT(t.path_id,',',ppl.id),
                    CONCAT(t.path,',',ppl.default_code),
                    t.pt_id,
                    t.pt_product,
                    ppl.id,
                    ppl.default_code,
                    imm.name,
                    mbl.location_id,
                    ROUND(t.qty * mbl.product_qty, 6)
                FROM bom_detail AS t
                JOIN mrp_bom AS mb ON t.id = mb.product_id
                JOIN mrp_bom_line AS mbl ON mbl.bom_id = mb.id
                JOIN product_product AS ppl ON ppl.id = mbl.product_id
                JOIN product_template AS ptl ON ptl.id = ppl.product_tmpl_id
                LEFT JOIN l10n_mx_immex_partida_type AS imm ON imm.id = ptl.immex_type_id)
            SELECT bd.pt_id, bd.pt_product,bd.id,bd.product, SUM(bd.qty) AS qty,COALESCE(pud.factor, -1) AS factor,TO_CHAR(CAST(NOW() AS DATE), 'DD/MM/YYYY')
            FROM bom_detail AS bd
            JOIN product_product AS pp ON bd.id = pp.id
            JOIN product_template AS pt ON pp.product_tmpl_id = pt.id
            LEFT JOIN product_uom_factor AS puf ON pt.uom_id = puf.unmed_origin_id
                AND pt.l10n_mx_edi_umt_aduana_id = puf.unmed_dest_id
            LEFT JOIN product_uom_details AS pud ON pp.id = pud.product_id
                AND puf.id = pud.uom_factor_id
            WHERE bd.immex IS NOT NULL
            GROUP BY bd.pt_id,bd.pt_product,bd.id,bd.product,pud.factor""" % (tuple(product_ids),))
        return self._cr.fetchall()


class ExportSiimmexBomInvoiceXlsx(models.AbstractModel):
    _name = 'report.immex_gebesa.export_siimex_bom_invoice_xlsx'
    _inherit = 'abstract.export.siimmex.bom.xlsx'

    def generate_xlsx_report(self, workbook, data, objects):
        workbook.set_properties({
            'comments': 'Created with Python and XlsxWriter from Odoo 12.0'})

        bold = workbook.add_format({'bold': True})

        sheet_bom = self.create_sheet_bom(workbook, bold)
        sheet_product = self.create_sheet_product(workbook, bold)

        row_bom = 2
        row_pro = 2
        list_products = []

        product_ids = objects.invoice_line_ids.mapped('product_id').mapped('id')

        for data in self.get_data_export(product_ids):
            parent_pp = self.env['product.product'].with_context(
                active_test=False).search([('id', '=', data[0])])
            child_pp = self.env['product.product'].with_context(
                active_test=False).search([('id', '=', data[2])])

            if data[5] < 0.00:
                raise ValidationError(
                    'No se encontro un factor de conversion para el producto %s de %s a %s' % (
                        child_pp.default_code, child_pp.uom_id.name,
                        child_pp.l10n_mx_edi_umt_aduana_id.name))

            if parent_pp.id not in list_products:
                self.insert_line_sheet_product(sheet_product, row_pro, parent_pp)
                list_products.append(parent_pp.id)
                row_pro += 1
            if child_pp.id not in list_products:
                self.insert_line_sheet_product(sheet_product, row_pro, child_pp)
                list_products.append(child_pp.id)
                row_pro += 1

            self.insert_line_sheet_bom(
                sheet_bom, row_bom, parent_pp, child_pp,
                data[4] * data[5], data[6])
            row_bom = row_bom + 1


class ExportSiimmexBomXlsx(models.AbstractModel):
    _name = 'report.immex_gebesa.export_siimex_bom_xlsx'
    _inherit = 'abstract.export.siimmex.bom.xlsx'

    def generate_xlsx_report(self, workbook, data, objects):
        workbook.set_properties({
            'comments': 'Created with Python and XlsxWriter from Odoo 12.0'})

        bold = workbook.add_format({'bold': True})

        sheet_bom = self.create_sheet_bom(workbook, bold)
        sheet_product = self.create_sheet_product(workbook, bold)

        row_bom = 2
        row_pro = 2
        list_products = []

        product_ids = objects.mapped('id')

        for data in self.get_data_export(product_ids):
            parent_pp = self.env['product.product'].with_context(
                active_test=False).search([('id', '=', data[0])])
            child_pp = self.env['product.product'].with_context(
                active_test=False).search([('id', '=', data[2])])

            if data[5] < 0.00:
                raise ValidationError(
                    'No se encontro un factor de conversion para el producto %s de %s a %s' % (
                        child_pp.default_code, child_pp.uom_id.name,
                        child_pp.l10n_mx_edi_umt_aduana_id.name))

            if parent_pp.id not in list_products:
                self.insert_line_sheet_product(sheet_product, row_pro, parent_pp)
                list_products.append(parent_pp.id)
                row_pro += 1
            if child_pp.id not in list_products:
                self.insert_line_sheet_product(sheet_product, row_pro, child_pp)
                list_products.append(child_pp.id)
                row_pro += 1

            self.insert_line_sheet_bom(
                sheet_bom, row_bom, parent_pp, child_pp,
                data[4] * data[5], data[6])
            row_bom = row_bom + 1
