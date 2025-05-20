# -*- coding: utf-8 -*-
# Copyright YEAR(S), AUTHOR(S)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api


class ParticularReport(models.AbstractModel):
    _name = 'report.paperwork_usa.report_usa'
    _description = 'descripcion pendiente'

    @api.multi
    def _get_report_values(self, docids, data=None):
        self.model = 'sale.order'

        planned_delivery_date = self.env.user.company_id.planned_delivery_date

        sales = self.env[self.model].search([
            ('id', 'in', docids)], order='name')
        docs = {}
        for sale in sales:
            client_order_ref = sale.client_order_ref or ''
            group_sale = str(sale.partner_id) + str(
                sale.partner_shipping_id) + client_order_ref
            if group_sale not in docs:
                docs[group_sale] = []
            docs[group_sale].append(sale)

            bom_lines = {}
            for line in sale.order_line:
                product = line.product_id
                if product:
                    bom = self.env['mrp.bom'].sudo().search([
                        ('product_id', '=', product.id),
                        ('type', '=', 'phantom')], limit=1)
                    if bom:
                        bom_lines[product.id] = bom.sudo().bom_line_ids
            shipment_date = False
            if sale.company_id.country_id.code != 'MX':
                mpf_order = self.env['sale.order'].sudo().search([('name', '=', sale.supplier_ref)])
                if mpf_order:
                    shipment_date = mpf_order.shipment_date
        docargs = {
            'doc_ids': docids,
            'doc_model': self.model,
            'docs': docs,
            'config': planned_delivery_date,
            'bom_lines': bom_lines,
            'shipment_date': shipment_date
        }
        return docargs
