# -*- coding: utf-8 -*-
# © <2019> <Armando Robledo>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ShipmentInstructionReport(models.AbstractModel):
    _name = 'report.report_shipment_instruction.report_shipment'
    _description = 'descripcion pendiente'

    @api.multi
    def _get_report_values(self, docids, data=None):
        self.model = 'mrp.shipment'

        user = self.env.user
        shipment = {}
        facturas = []
        docs = self.env[self.model].browse(docids)
        busquedacompany = self.env['res.company'].search(
            [('id', '=', user.id)])

        for ship in docs:
            shipment[ship.id] = []
            for line in ship.line_ids:
                invoices = self.env['account.invoice'].search([
                    ('sale_id', '=', line.sale_order_id.id)])
                for inv in invoices:
                    facturas.append(inv)

                if line.product_id and line.product_id.family_id:
                    busqueda = self.env['stock.location.route'].search([
                        ('family_ids', '=', line.product_id.family_id.id)])
                    if busqueda.id == 56:
                        shipment[line.id].append(line.product_id)
        docargs = {
            'doc_ids': docids,
            'doc_model': self.model,
            'docs': docs,
            'shipment': shipment,
            'facturas': facturas,
            'busquedacompany': busquedacompany,
        }
        return docargs
