# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ParticularReport(models.AbstractModel):
    _name = 'report.mrp_shipment.report_shipment_barcode'
    _description = 'descripcion pendiente'

    @api.multi
    def _get_report_values(self, docids, data=None):
        self.model = 'mrp.shipment'
        bom_obj = self.env['mrp.bom']
        docs = self.env[self.model].browse(docids)
        shipment = {}
        kit = {}

        for ship in docs:
            shipment[ship.id] = {}
            for line in ship.line_ids:
                family = line.product_id.family_id.name
                partner = line.partner_id.name
                city = line.city
                if family not in shipment[ship.id].keys():
                    shipment[ship.id][family] = {}
                if partner not in shipment[ship.id][family].keys():
                    shipment[ship.id][family][partner] = {}
                if city not in shipment[ship.id][family][partner].keys():
                    shipment[ship.id][family][partner][city] = []
                shipment[ship.id][family][partner][city].append(line)
                bom = bom_obj.search([('product_id', '=', line.product_id.id),
                                      ('type', '=', 'phantom')])
                if bom:
                    if line.product_id.id not in kit.keys():
                        kit[line.product_id.id] = bom

        docargs = {
            'doc_ids': docids,
            'doc_model': self.model,
            'docs': docs,
            'shipment': shipment,
            'kit': kit,
            'picking_open': self._picking_open,
        }
        return docargs

    def _picking_open(self, order):
        picking_obj = self.env['stock.picking']
        location_obj = self.env['stock.location']
        location = location_obj.search([('usage', '=', 'customer')])
        picking = picking_obj.search([
            ('group_id', '=', order.procurement_group_id.id),
            ('location_dest_id', 'in', location.mapped('id')),
            ('state', 'not in', ['done', 'cancel'])
        ], limit=1)
        return picking.name or False
