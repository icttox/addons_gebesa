# Copyright 2020, Cesar Barron
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


class ExportSiimmexXlsx(models.AbstractModel):
    _name = 'report.immex_gebesa.export_siimex_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, objects):
        workbook.set_properties({
            'comments': 'Created with Python and XlsxWriter from Odoo 12.0'})
        sheet = workbook.add_worksheet('Lista de Materiales')
        sheet.set_landscape()
        sheet.fit_to_pages(1, 0)
        sheet.set_zoom(90)
        bold = workbook.add_format({'bold': True})

        sheet.write('A1', 'MATERIAL PADRE', bold)
        sheet.write('B1', 'NOMBRE ESTRUCTURA', bold)
        sheet.write('C1', 'FECHA INICIAL', bold)
        sheet.write('D1', 'MATERIAL HIJO', bold)
        sheet.write('E1', 'CANTIDAD UTILIZADA', bold)
        sheet.write('F1', 'PORCENTAJE MERMA', bold)
        sheet.write('G1', 'PORCENTAJE DESPERDICIO', bold)
        rownum = 2
        list_bom = []
        for route in self._get_data_export():
            padre = False
            hijo = False
            for product in route[0].split(','):
                padre = hijo
                hijo = product
                if padre and hijo:
                    self._cr.execute("""
                        SELECT
                            pp.default_code,
                            CONCAT(
                                SUBSTRING(pp.default_code, 1, 3), '-',
                                SUBSTRING(ppl.default_code, 1, 3), '-',
                                CAST(mbl.id AS TEXT)),
                            '01/01/2000',
                            ppl.default_code,
                            ROUND(mbl.product_qty, 6),
                            0,
                            0
                        FROM product_product AS pp
                        JOIN mrp_bom AS mb ON pp.id = mb.product_id
                        JOIN mrp_bom_line AS mbl ON mbl.bom_id = mb.id
                        JOIN product_product AS ppl ON mbl.product_id = ppl.id
                        WHERE pp.id = %s AND ppl.id = %s
                    """, (str(padre), str(hijo)))
                    for line in self._cr.fetchall():
                        uniq = (line[0], line[3], str(line[4]))
                        if uniq not in list_bom:
                            sheet.write('A' + str(rownum), line[0])
                            sheet.write('B' + str(rownum), line[1])
                            sheet.write('C' + str(rownum), line[2])
                            sheet.write('D' + str(rownum), line[3])
                            sheet.write('E' + str(rownum), line[4])
                            sheet.write('F' + str(rownum), line[5])
                            sheet.write('G' + str(rownum), line[6])
                            rownum = rownum + 1
                            list_bom.append(uniq)

    def _get_data_export(self):
        self._cr.execute("""
            WITH RECURSIVE bom_detail(path_id,path,id,product,immex,location_id) AS(
                SELECT
                    CAST(pp.id AS TEXT),
                    pp.default_code,
                    pp.id,
                    pp.default_code,
                    imm.name,
                    0
                FROM product_product AS pp
                JOIN product_template AS pt ON pt.id = pp.product_tmpl_id
                LEFT JOIN l10n_mx_immex_partida_type AS imm ON imm.id = pt.immex_type_id
                WHERE pp.salida_a24
                UNION SELECT
                    CONCAT(t.path_id,',',ppl.id),
                    CONCAT(t.path,',',ppl.default_code),
                    ppl.id,
                    ppl.default_code,
                    imm.name,
                    mbl.location_id
                FROM bom_detail AS t
                JOIN mrp_bom AS mb ON t.id = mb.product_id
                JOIN mrp_bom_line AS mbl ON mbl.bom_id = mb.id
                JOIN product_product AS ppl ON ppl.id = mbl.product_id
                JOIN product_template AS ptl ON ptl.id = ppl.product_tmpl_id
                LEFT JOIN l10n_mx_immex_partida_type AS imm ON imm.id = ptl.immex_type_id)
            SELECT *
            FROM bom_detail AS bd
            WHERE bd.immex IS NOT NULL""")
        return self._cr.fetchall()
