# -*- coding: utf-8 -*-
# Copyright YEAR(S), AUTHOR(S)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ParticularReport(models.AbstractModel):
    _name = 'report.paperwork_usa.bill_ladind_report'
    _description = 'descripcion pendiente'

    @api.multi
    def _get_report_values(self, docids, data=None):
        self.model = 'mrp.shipment'
        bom_obj = self.env['mrp.bom']
        docs = self.env[self.model].browse(docids)
        kit = {}

        for line in docs.line_ids:
            bom = bom_obj.search([('product_id', '=', line.product_id.id),
                                  ('type', '=', 'phantom')])
            if bom:
                if line.product_id.id not in kit.keys():
                    kit[line.product_id.id] = bom

        docargs = {
            'doc_ids': docids,
            'doc_model': self.model,
            'docs': docs,
            'kit': kit,
        }
        return docargs
