# -*- coding: utf-8 -*-
# © <2018> <Aldo Nerio>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ParticularReport(models.AbstractModel):
    _name = 'report.fletera_externa.report_fletera_externa'
    _description = 'descripcion pendiente'

    @api.multi
    def _get_report_values(self, docids, data=None):
        self.model = 'mrp.shipment'
        shipment_var = self.env[self.model].browse(docids)
        clientes = {}
        for shipment in shipment_var:
            partners = []
            for sale in shipment.sale_ids:
                if sale.partner_id not in partners:
                    partners.append(sale.partner_id)
            clientes[shipment.id] = partners
        docargs = {
            'doc_ids': docids,
            'docs': shipment_var,
            'doc_model': self.model,
            'clientes': clientes
        }
        return docargs
