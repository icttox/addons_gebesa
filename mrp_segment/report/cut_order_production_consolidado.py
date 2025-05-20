# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ParticularReport(models.AbstractModel):
    _name = 'report.mrp_segment.report_cut_order_production_consolidado'
    _description = 'descripcion pendiente'

    @api.multi
    def _get_report_values(self, docids, data=None):
        self.model = 'mrp.production'
        # report_obj = self.env['report']
        # report = report_obj._get_report_from_name(
        #    'mrp_segment.report_cut_order_production_consolidado')
        obj_production = self.env[self.model]
        mrp_production = obj_production.browse(docids)
        count = 0
        keys = {}
        docs = []
        for production in mrp_production:
            product = production.product_id
            if product.id not in keys.keys():
                keys[product.id] = count
                docs.append({
                    'name': production.name,
                    'folio': None,
                    'products': {},
                })
                docs[count]['products'][product.id] = {
                    'product_name': product.name,
                    'product_qty': production.product_qty,
                    'product_code': product.default_code,
                    'cut_line': {}
                }
                count = count + 1
            else:
                docs[keys[product.id]]['name'] += ', ' + production.name
                docs[keys[product.id]]['products'][product.id][
                    'product_qty'] += production.product_qty
            bom_lines = production.bom_id.bom_line_ids
            for bom_line in bom_lines:
                for bom_line_det in bom_line.bom_line_detail_ids:
                    prod_line = bom_line_det.production_line_id.description
                    if prod_line not in docs[keys[product.id]]['products'][
                            product.id]['cut_line'].keys():
                        docs[keys[product.id]]['products'][
                            product.id]['cut_line'][prod_line] = []
                    add = True
                    for cut in docs[keys[product.id]]['products'][product.id][
                            'cut_line'][prod_line]:
                        if cut['name'] == bom_line_det.name and \
                                cut['row'] == bom_line_det.row and \
                                cut['caliber'] == bom_line_det.caliber_id and \
                                cut['width'] == bom_line_det.width_cut and \
                                cut['long'] == bom_line_det.long_cut:
                            cut['qty'] += bom_line_det.quantity * \
                                production.product_qty
                            add = False
                    if add:
                        docs[keys[product.id]]['products'][product.id][
                            'cut_line'][prod_line].append({
                                'name': bom_line_det.name,
                                'row': bom_line_det.row,
                                'caliber': bom_line_det.caliber_id,
                                'width': bom_line_det.width_cut,
                                'long': bom_line_det.long_cut,
                                'qty': (bom_line_det.quantity *
                                        production.product_qty)
                            })

        for doc in docs:
            for product in doc['products'].keys():
                for prod_line in doc['products'][product]['cut_line'].keys():
                    doc['products'][product]['cut_line'][prod_line] = sorted(
                        doc['products'][product]['cut_line'][prod_line],
                        key=lambda cut: cut['long'])
                    doc['products'][product]['cut_line'][prod_line] = sorted(
                        doc['products'][product]['cut_line'][prod_line],
                        key=lambda cut: cut['width'])
                    doc['products'][product]['cut_line'][prod_line] = sorted(
                        doc['products'][product]['cut_line'][prod_line],
                        key=lambda cut: cut['caliber'].key_caliber)
                    doc['products'][product]['cut_line'][prod_line] = sorted(
                        doc['products'][product]['cut_line'][prod_line],
                        key=lambda cut: cut['name'])
                    doc['products'][product]['cut_line'][prod_line] = sorted(
                        doc['products'][product]['cut_line'][prod_line],
                        key=lambda cut: cut['row'])

        docargs = {
            'doc_ids': docids,
            # 'doc_model': report.model,
            'doc_model': self.model,
            'docs': docs,
        }

        # return report_obj.render(
        #     'mrp_segment.report_cut_order_production_consolidado',
        #     docargs)
        return docargs
