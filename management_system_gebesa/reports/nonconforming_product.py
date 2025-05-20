# Copyright 2022, Cesar Barron
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import logging
import base64
import io
from odoo import models, tools
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)
_colors = {
    1: '#ffffcc',
    2: '#ddebf7',
    3: '#ffe699',
    4: '#fce4d6',
    5: '#f4b084',
    6: '#bfbfbf',
    7: '#c6e0b4',
    8: '#d6dce4',
    9: '#cccc00',
}


def copy_format(book, fmt):
    properties = [f[4:] for f in dir(fmt) if f[0:4] == 'set_']
    dft_fmt = book.add_format()
    res = book.add_format(
        {k: v for k, v in fmt.__dict__.items() if k in properties and dft_fmt.__dict__[k] != v})
    return res


class NonconformingProductXlsx(models.AbstractModel):
    _name = 'report.management_system_gebesa.nonconforming_product_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def get_formats(self, workbook):
        formats = {}

        formats['title'] = workbook.add_format({
            'align': 'center',
            'bold': 1,
            'font_size': 18,
            'valign': 'vcenter',
        })

        formats['subtitle'] = workbook.add_format({
            'bold': 1,
            'font_size': 12,
            'valign': 'vcenter',
        })

        formats['title_table'] = workbook.add_format({
            'align': 'center',
            'bg_color': "#c9c9c9",
            'bold': 1,
            'border': 2,
            'font_size': 10,
            'text_wrap': True,
            'valign': 'vcenter',
        })

        for col in _colors:
            formats['title_worcenter' + str(col)] = workbook.add_format({
                'align': 'center',
                'bg_color': _colors[col],
                'bold': 1,
                'border': 2,
                'font_size': 22,
                'rotation': 90,
                'valign': 'vcenter',
            })

        formats['data'] = workbook.add_format({
            'border': 1,
            'font_size': 9,
        })

        formats['data_start'] = workbook.add_format({
            'top': 2,
            'right': 1,
            'bottom': 1,
            'font_size': 9,
        })

        formats['total'] = workbook.add_format({
            'top': 1,
            'right': 1,
            'bottom': 2,
            'font_size': 14,
            'valign': 'top',
        })

        return formats

    def generate_xlsx_report(self, workbook, data, objects):
        workbook.set_properties({
            'comments': 'Created with Python and XlsxWriter from Odoo 12.0'})
        sheet = workbook.add_worksheet(_('Sheet'))

        sheet.set_landscape()
        sheet.fit_to_pages(1, 0)
        sheet.set_zoom(115)

        sheet.set_column(0, 2, 4)
        sheet.set_column(3, 3, 22)
        sheet.set_column(4, 4, 14)
        sheet.set_column(5, 5, 39)
        sheet.set_column(6, 9, 9)
        sheet.set_row(0, 40)
        sheet.set_row(5, 25)

        formats = self.get_formats(workbook)

        if self.env.user.company_id.logo_invoice:
            logo = tools.image_get_resized_images(
                self.env.user.company_id.logo_invoice,
                avoid_resize_medium=True,
                sizes={'image_medium': (130, 40)})
            sheet.insert_image('A1:A2', "image.png", {
                'image_data': io.BytesIO(base64.b64decode(logo['image_medium'])),
                'x_offset': 10, 'y_offset': 5})
        sheet.merge_range(
            'A1:J1', 'Reporte Interno de Producto No Conforme', formats['title'])

        sheet.merge_range(
            'A2:D2', 'Planta:', formats['subtitle'])
        sheet.write('E2', 'Semana:', formats['subtitle'])

        sheet.merge_range(
            'A3:D3', 'Responsable:', formats['subtitle'])
        sheet.write('E3', 'Periodo:', formats['subtitle'])
        sheet.merge_range(
            'G3:I3', 'Total de piezas revisadas:', formats['subtitle'])

        sheet.merge_range(
            'A4:B4', 'Objetivo:', formats['subtitle'])
        sheet.merge_range(
            'C4:D4', 'No más del 3.5% por defecto:')
        sheet.write('E4', '% Def. Semana:', formats['subtitle'])
        sheet.merge_range(
            'G4:I4', 'Total de piezas rechazadas:', formats['subtitle'])

        sheet.merge_range(
            'A6:B6', 'Área de inspección', formats['title_table'])
        sheet.merge_range(
            'C6:D6', 'Defecto', formats['title_table'])
        sheet.write('E6', '', formats['title_table'])
        sheet.write('F6', '', formats['title_table'])
        sheet.write('G6', '%Por defecto', formats['title_table'])
        sheet.write('H6', '% Defectos por área', formats['title_table'])
        sheet.write('I6', 'Piezas revisadas', formats['title_table'])
        sheet.write('J6', 'Total rechazadas', formats['title_table'])

        workcenter_ids = self.env['mrp.workcenter'].search([
            ('website_published', '=', True)])

        last_row = 7
        row = last_row
        num_color = 1
        total_rev = 0
        total_rej = 0

        for workcenter in workcenter_ids:
            flaw_ids = self.env['quality.alert.flaw'].search([
                ('workcenter_ids', '=', workcenter.id)])

            total_workcenter_rev = 0
            total_workcenter_rej = 0
            distinct = []
            alert = objects.filtered(lambda alt: alt.workcenter_id.id == workcenter.id)
            for alt in alert:
                total_workcenter_rej += alt.qty_rejected
                key = str(alt.product_id.id) + '|' + str(alt.qty_reviewed) + '|'
                if alt.sale_id:
                    key += str(alt.sale_id.id)
                else:
                    key += 'N/A'
                if key not in distinct:
                    total_workcenter_rev += alt.qty_reviewed
                    distinct.append(key)

            first_data = True

            for flaw in flaw_ids:
                form = formats['data']
                if first_data:
                    form = formats['data_start']
                    first_data = False
                sheet.write('C' + str(row), flaw.code, form)
                sheet.write('D' + str(row), flaw.name, form)

                alert = objects.filtered(lambda alt: alt.flaw_id.id == flaw.id)
                products = ''
                alt_total = 0

                for alt in alert:
                    products += str(alt.qty_rejected) + ')' + alt.product_id.name + '\n'
                    alt_total += alt.qty_rejected

                if alt_total > 0:
                    sheet.write('E' + str(row), alt_total, form)
                    sheet.write('F' + str(row), products, form)
                    percent = 0
                    if total_workcenter_rev > 0:
                        percent = alt_total / total_workcenter_rev
                    percent = percent * 100
                    sheet.write(
                        'G' + str(row),
                        '{0:.2f}'.format(percent) + '%', form)
                else:
                    sheet.write('E' + str(row), '', form)
                    sheet.write('F' + str(row), '', form)
                    sheet.write('G' + str(row), '', form)

                row += 1

            sheet.merge_range(
                'A' + str(last_row) + ':B' + str(row - 1),
                workcenter.name, formats['title_worcenter' + str(num_color)])

            percent_workcenter = 0
            if total_workcenter_rev > 0 and total_workcenter_rej > 0:
                percent_workcenter = total_workcenter_rej / total_workcenter_rev
            percent_workcenter = percent_workcenter * 100

            sheet.merge_range(
                'H' + str(last_row) + ':H' + str(row - 1),
                '{0:.2f}'.format(percent_workcenter) + '%', formats['total'])
            sheet.merge_range(
                'I' + str(last_row) + ':I' + str(row - 1),
                total_workcenter_rev, formats['total'])
            sheet.merge_range(
                'J' + str(last_row) + ':J' + str(row - 1),
                total_workcenter_rej, formats['total'])

            last_row = row
            num_color += 1
            if num_color > 9:
                num_color = 1

            total_rev += total_workcenter_rev
            total_rej += total_workcenter_rej

        total_perc = 0
        if total_rej > 0 and total_rev > 0:
            total_perc = total_rej / total_rev
        total_perc = total_perc * 100

        sheet.write('J3', total_rev, formats['subtitle'])
        sheet.write('F4', '{0:.2f}'.format(total_perc) + '%', formats['subtitle'])
        sheet.write('J4', total_rej, formats['subtitle'])
