# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models
from odoo.tools import image


class ParticularReport(models.AbstractModel):
    _name = 'report.mrp_shipment.report_shipment'
    _description = 'descripcion pendiente'

    @api.multi
    def search_kit(self, product_id):
        self._cr.execute(
            """
            WITH RECURSIVE componentes(
                    product_id, code, name, qty, family, not_kit, r, producto_en) AS (
                SELECT
                    pp.id,
                    pp.default_code,
                    COALESCE(ir.value, pp.individual_name, ir2.value,
                        pp.name_template, 'Sin definir') as producto,
                    ROUND((mbl.product_qty / mb.product_qty)
                        * 1,6) AS product_qty,
                    pf.name,
                    CASE WHEN mb2.type = 'phantom'
                        THEN FALSE
                        ELSE TRUE END AS not_kit,
                    CAST(ROW_NUMBER () OVER () AS TEXT),
                    COALESCE(ir_en.value, pp.individual_name, ir2_en.value,
                        pp.name_template, 'Sin definir') as producto_en
                FROM mrp_bom AS mb
                JOIN mrp_bom_line AS mbl ON mb.id = mbl.bom_id
                JOIN product_product AS pp ON mbl.product_id = pp.id
                JOIN product_template AS pt ON pp.product_tmpl_id = pt.id
                LEFT JOIN product_family AS pf ON pt.family_id = pf.id
                LEFT JOIN ir_translation AS ir ON ir.res_id = pp.id
                    AND ir.lang = 'es_MX'
                    AND ir.name = 'product.product,individual_name'
                LEFT JOIN ir_translation AS ir2 ON pt.id = ir2.res_id
                    AND ir2.lang = 'es_MX'
                    AND ir2.name = 'product.template,name'
                LEFT JOIN ir_translation AS ir_en ON ir.res_id = pp.id
                    AND ir.lang = 'en_US'
                    AND ir.name = 'product.product,individual_name'
                LEFT JOIN ir_translation AS ir2_en ON pt.id = ir2.res_id
                    AND ir2.lang = 'en_US'
                    AND ir2.name = 'product.template,name'
                LEFT JOIN mrp_bom AS mb2 ON pp.id = mb2.product_id
                    AND mb2.active IS TRUE
                WHERE mb.product_id = %s AND mb.type = 'phantom'
                    AND mb.active IS TRUE
                UNION SELECT
                    pp.id,
                    pp.default_code,
                    COALESCE(ir.value, pp.individual_name, ir2.value,
                        pp.name_template, 'Sin definir') as producto,
                    ROUND(c.qty * ((mbl.product_qty / mb.product_qty)
                        * 1), 6) AS product_qty,
                    pf.name,
                    CASE WHEN mb2.type = 'phantom'
                        THEN FALSE
                        ELSE TRUE END AS not_kit,
                    CONCAT(c.r, '-', CAST(ROW_NUMBER () OVER () AS TEXT)),
                    COALESCE(ir_en.value, pp.individual_name, ir2_en.value,
                        pp.name_template, 'Sin definir') as producto_en
                FROM componentes AS c
                LEFT JOIN mrp_bom AS mb ON c.product_id = mb.product_id
                    AND mb.active IS TRUE
                JOIN mrp_bom_line AS mbl ON mb.id = mbl.bom_id
                JOIN product_product AS pp ON mbl.product_id = pp.id
                JOIN product_template AS pt ON pp.product_tmpl_id = pt.id
                LEFT JOIN product_family AS pf ON pt.family_id = pf.id
                LEFT JOIN ir_translation AS ir ON ir.res_id = pp.id
                    AND ir.lang = 'es_MX'
                    AND ir.name = 'product.product,individual_name'
                LEFT JOIN ir_translation AS ir2 ON pt.id = ir2.res_id
                    AND ir2.lang = 'es_MX'
                    AND ir2.name = 'product.template,name'
                LEFT JOIN ir_translation AS ir_en ON ir.res_id = pp.id
                    AND ir.lang = 'en_US'
                    AND ir.name = 'product.product,individual_name'
                LEFT JOIN ir_translation AS ir2_en ON pt.id = ir2.res_id
                    AND ir2.lang = 'en_US'
                    AND ir2.name = 'product.template,name'
                JOIN mrp_bom AS mb2 ON pp.id = mb2.product_id
                    AND mb2.active IS TRUE
                WHERE c.not_kit IS false
            )
            SELECT product_id, code, name, SUM(qty), family, producto_en
            FROM componentes
            WHERE not_kit
            GROUP BY product_id, code, name, family, producto_en
            ORDER BY producto_en, code, product_id""",
            ([product_id.id]))
        return self._cr.fetchall()

    @api.multi
    def search_range_packing(self, line, num_packing):
        data = {
            'total_page': 0,
            'min_page': num_packing,
            'max_page': num_packing,
        }
        return data

    @api.multi
    def _get_report_values(self, docids, data=None):
        self.model = 'mrp.shipment'
        docs = self.env[self.model].browse(docids)
        shipment = {}
        shipment1 = {}
        packing_line = {}
        kit = {}

        for ship in docs:
            num_packing = 0
            shipment[ship.id] = {}
            shipment1[ship.id] = {}

            for line in ship.line_ids:
                family = line.product_id.family_id.name
                partner = line.partner_id.name
                so = line.sale_order_id.name + ' (' + line.sale_order_id.client_order_ref + ')'
                city = line.city

                if family not in shipment1[ship.id].keys():
                    shipment1[ship.id][family] = []

                if partner not in shipment[ship.id].keys():
                    shipment[ship.id][partner] = {}

                if so not in shipment[ship.id][partner].keys():
                    shipment[ship.id][partner][so] = {}

                if city not in shipment[ship.id][partner][so].keys():
                    shipment[ship.id][partner][so][city] = []

                shipment1[ship.id][family].append(line)

                shipment[ship.id][partner][so][city].append(line)

                componentes = self.search_kit(line.product_id)
                if componentes:
                    if line.product_id.id not in kit.keys():
                        kit[line.product_id.id] = componentes

                range_packing = self.search_range_packing(line, num_packing)
                num_packing += range_packing['total_page']
                packing_line[line.id] = range_packing

        company_logo = False
        if self.env.user.company_id.logo:
            company_logo = image.crop_image(
                self.env.user.company_id.logo,
                type='top',
                ratio=(5, 3),
                size=(500, 400))

        docargs = {
            'doc_ids': docids,
            'doc_model': self.model,
            'docs': docs,
            'shipment': shipment,
            'shipment1': shipment1,
            'kit': kit,
            'packing_line': packing_line,
            'company_logo': company_logo
        }
        return docargs
