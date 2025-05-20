# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ParticularReportTsca(models.AbstractModel):
    _name = 'report.paperwork_usa.report_tsca_format'
    _description = 'descripcion pendiente'

    @api.multi
    def _get_report_values(self, docids, data=None):
        self.model = 'mrp.shipment'
        shipments = self.env[self.model].browse(docids)
        docs = []
        products = {}
        for ship in shipments:
            self._cr.execute(
                """
                    WITH RECURSIVE bom_detail(msl_id,master_product_id,product_id,mp,tsca) AS(
                        SELECT
                            msl.id,
                            pp.id,
                            pp.id,
                            FALSE,
                            pp.is_tsca
                        FROM mrp_shipment AS ms
                        JOIN mrp_shipment_line AS msl ON ms.id = msl.shipment_id
                        JOIN product_product AS pp ON msl.product_id = pp.id
                        WHERE ms.id = %s
                        UNION SELECT
                            bd.msl_id,
                            bd.master_product_id,
                            pp.id,
                            CASE WHEN mb2.id IS NULL THEN TRUE ELSE FALSE END,
                            pp.is_tsca
                        FROM bom_detail AS bd
                        LEFT JOIN mrp_bom AS mb on bd.product_id = mb.product_id
                            AND mb.company_id = %s AND mb.active IS True
                        LEFT JOIN mrp_bom_line AS mbl on mb.id = mbl.bom_id
                        LEFT JOIN product_product AS pp ON mbl.product_id = pp.id
                        LEFT JOIN mrp_bom AS mb2 on pp.id = mb2.product_id
                            AND mb2.company_id = mb.company_id AND mb2.active IS True)
                    SELECT
                        master_product_id
                    FROM bom_detail
                    WHERE mp IS TRUE
                        AND tsca IS TRUE
                    GROUP BY master_product_id
                """, (str(ship.id), str(self.env.user.company_id.id)))
            product_ids = self._cr.fetchall()
            if product_ids:
                docs.append(ship.id)
                products[ship.id] = []
                for prod in product_ids:
                    products[ship.id].append(self.env['product.product'].browse(prod[0]))

        docargs = {
            'doc_ids': docs,
            'doc_model': self.model,
            'docs': self.env[self.model].browse(docs),
            'products': products
        }
        return docargs
