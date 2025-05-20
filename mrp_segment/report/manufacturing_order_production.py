# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ParticularReport(models.AbstractModel):
    _name = 'report.mrp_segment.report_manufacturing_order_production'
    _description = 'descripcion pendiente'

    @api.multi
    def _get_report_values(self, docids, data=None):
        self.model = 'mrp.production'
        production = self.env[self.model].browse(docids)
        docs = []
        for doc in production:
            lines = []
            mp_lines = []
            groups = {}
            mp_groups = {}
            products = {}
            mp_products = {}
            pedidos = []
            fabricacion = doc.name
            line_id = doc.product_id.line_id
            group_id = doc.product_id.group_id
            if line_id not in lines:
                lines.append(line_id)
                groups[line_id.id] = []
            if group_id not in groups[line_id.id]:
                groups[line_id.id].append(group_id)
                products[str(line_id.id) + '-' + str(group_id.id)] = []
            products[str(line_id.id) + '-' + str(group_id.id)].append({
                'id': doc.product_id.id,
                'product_code': doc.product_id.default_code,
                'product_name': doc.product_id.name,
                'individual_name': doc.product_id.individual_name,
                'standard_cost': doc.product_id.standard_price,
                'product_qty': doc.product_qty,
            })
            if doc.sale_id not in pedidos:
                pedidos.append(doc.sale_id)
            product_lines_ids = sorted(
                doc.move_raw_ids,
                key=lambda line: line.id)

            for move_raw in product_lines_ids:
                line_id = move_raw.product_id.line_id
                group_id = move_raw.product_id.group_id
                if line_id not in mp_lines:
                    mp_lines.append(line_id)
                    mp_groups[line_id.id] = []
                if group_id not in mp_groups[line_id.id]:
                    mp_groups[line_id.id].append(group_id)
                    mp_products[str(line_id.id) + '-' + str(group_id.id)] = []
                add = True

                for prod in mp_products[
                        str(line_id.id) + '-' + str(group_id.id)]:
                    if move_raw.product_id.id == prod['id']:
                        prod['product_qty'] = prod[
                            'product_qty'] + move_raw.product_qty
                        prod['standard_cost'] = move_raw.product_id.standard_price
                        add = False
                if add:
                    mp_products[
                        str(line_id.id) + '-' + str(group_id.id)].append({
                            'id': move_raw.product_id.id,
                            'location': move_raw.location_id.name,
                            'product_code': move_raw.product_id.default_code,
                            'product_name': move_raw.product_id.name,
                            'individual_name': move_raw.product_id.individual_name,
                            'standard_cost': move_raw.product_id.standard_price,
                            'product_qty': move_raw.product_qty,
                            'uom': move_raw.product_uom.name,
                        })

            docs.append({
                'date': doc.date_planned_start,
                'state': doc.state,
                'folio': doc.name,
                'location_dest_id': doc.location_dest_id.name,
                'lines': lines,
                'groups': groups,
                'products': products,
                'pedidos': pedidos,
                'mp_lines': mp_lines,
                'mp_groups': mp_groups,
                'mp_products': mp_products,
                'fabricacion': fabricacion,
            })

        docargs = {
            'doc_ids': self._ids,
            'doc_model': self.model,
            'docs': docs,
        }

        return docargs
