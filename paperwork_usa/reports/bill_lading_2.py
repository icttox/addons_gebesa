# -*- coding: utf-8 -*-
# Copyright YEAR(S), AUTHOR(S)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api


class ParticularReport(models.AbstractModel):
    _name = 'report.paperwork_usa.report_bill_lading_2'
    _description = 'descripcion pendiente'

    @api.multi
    def _get_report_values(self, docids, data=None):
        self.model = 'mrp.shipment'
        shipment_ids = self.env[self.model].browse(docids)
        bom_obj = self.env['mrp.bom']
        data = {}
        kit = {}
        for shipment in shipment_ids:
            data[shipment.id] = {}
            for line in shipment.line_ids:
                bom = bom_obj.search([
                    ('product_id', '=', line.product_id.id),
                    ('type', '=', 'phantom')])
                if bom:
                    if line.product_id.id not in kit.keys():
                        kit[line.product_id.id] = bom
                partner = line.partner_shipping_id
                if partner.id not in data[shipment.id].keys():
                    data[shipment.id][partner.id] = {}
                    data[shipment.id][partner.id]['partner'] = partner
                    data[shipment.id][partner.id]['order'] = []
                    data[shipment.id][partner.id]['order_line'] = []
                    data[shipment.id][partner.id]['ship_line'] = []
                if line.sale_order_id not in data[shipment.id][partner.id]['order']:
                    data[shipment.id][partner.id]['order'].append(line.sale_order_id)
                if line.order_line_id not in data[shipment.id][partner.id]['order_line']:
                    data[shipment.id][partner.id]['order_line'].append(line.order_line_id)
                if line not in data[shipment.id][partner.id]['ship_line']:
                    data[shipment.id][partner.id]['ship_line'].append(line)

        docargs = {
            'doc_ids': docids,
            'doc_model': self.model,
            'docs': shipment_ids,
            'data': data,
            'kits': kit
        }
        return docargs
