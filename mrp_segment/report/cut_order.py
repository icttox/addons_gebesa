# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models
from odoo.exceptions import UserError


class ParticularReport(models.AbstractModel):
    _name = 'report.mrp_segment.report_cut_order'
    _description = 'descripcion pendiente'

    @api.multi
    def _get_report_values(self, docids, data=None):
        self.model = 'mrp.segment'
        #report_obj = self.env['report']
        #report = report_obj._get_report_from_name(
        #    'mrp_segment.report_cut_order')
        obj_segment = self.env[self.model]
        segments = obj_segment.browse(docids)
        docs = []
        for seg in segments:
            products = {}
            for seg_line in seg.line_ids:
                production = seg_line.mrp_production_id
                product = production.product_id
                if production.product_id.id in products:
                    products[product.id]['product_qty'] += \
                        production.product_qty
                else:
                    products[product.id] = {
                        'product_name': product.name,
                        'product_qty': production.product_qty,
                        'product_code': product.default_code,
                        'cut_line': {}
                    }
                bom_lines = production.bom_id.bom_line_ids
                for bom_line in bom_lines:
                    for bom_line_det in bom_line.bom_line_detail_ids:
                        if not bom_line_det.name:
                            raise UserError(
                                'Un detalle de la linea %s del producto %s no tiene nombre \n \
                                Por favor comuníquese con el departamento de claves' % (
                                    bom_line.product_id.display_name,
                                    production.product_id.display_name))
                        if not bom_line_det.caliber_id:
                            raise UserError(
                                'El detalle %s de la linea %s del producto %s no tiene calibre \n \
                                Por favor comuníquese con el departamento de claves' % (
                                    bom_line_det.name, bom_line.product_id.display_name,
                                    production.product_id.display_name))
                        prod_line = bom_line_det.production_line_id.description
                        if prod_line not in products[product.id][
                                'cut_line'].keys():
                            products[product.id]['cut_line'][prod_line] = []
                        add = True
                        for cut in products[product.id]['cut_line'][prod_line]:
                            if cut['name'] == bom_line_det.name and \
                                    cut['row'] == bom_line_det.row and \
                                    cut['caliber'] == bom_line_det.caliber_id and \
                                    cut['width'] == bom_line_det.width_cut and \
                                    cut['long'] == bom_line_det.long_cut:
                                cut['qty'] += bom_line_det.quantity * \
                                    production.product_qty
                                add = False
                        if add:
                            products[product.id]['cut_line'][prod_line].append({
                                'name': bom_line_det.name,
                                'row': bom_line_det.row,
                                'caliber': bom_line_det.caliber_id,
                                'width': bom_line_det.width_cut,
                                'long': bom_line_det.long_cut,
                                'qty': bom_line_det.quantity * production.product_qty
                            })
                for product in products:
                    for prod_line in products[product]['cut_line'].keys():
                        products[product]['cut_line'][prod_line] = sorted(
                            products[product]['cut_line'][prod_line],
                            key=lambda cut: cut['long'])
                        products[product]['cut_line'][prod_line] = sorted(
                            products[product]['cut_line'][prod_line],
                            key=lambda cut: cut['width'])
                        products[product]['cut_line'][prod_line] = sorted(
                            products[product]['cut_line'][prod_line],
                            key=lambda cut: cut['caliber'].key_caliber)
                        products[product]['cut_line'][prod_line] = sorted(
                            products[product]['cut_line'][prod_line],
                            key=lambda cut: cut['name'])
                        products[product]['cut_line'][prod_line] = sorted(
                            products[product]['cut_line'][prod_line],
                            key=lambda cut: cut['row'])

            docs.append({
                'name': seg.name,
                'folio': seg.folio,
                'products': products,
            })

        docargs = {
            'doc_ids': docids,
            #'doc_model': report.model,
            'doc_model': self.model,
            'docs': docs,
        }

        #return report_obj.render(
        #    'mrp_segment.report_cut_order', docargs)
        return docargs
