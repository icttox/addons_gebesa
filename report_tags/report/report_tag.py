# -*- coding: utf-8 -*-
#  <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ParticularReport(models.AbstractModel):
    _name = 'report.report_tags.report_tag1'
    _description = 'Report Tags'

    def get_line_qty(self, productions):
        line_qty = {}
        for doc in productions:
            if doc not in line_qty:
                line_qty[doc.id] = {doc.sale_line_id: doc.product_qty}
        return line_qty

    @api.multi
    def _get_report_values(self, docids, data=None):
        production = self.env['mrp.production'].browse(docids)
        cust_code = {}
        for prod in production:
            cust_code[prod.id] = {}
            customer_code = self.env['product.product.customer'].search(
                [('product_id', '=', prod.product_id.id),
                 ('partner_id', '=', prod.partner_id.id)])

            if customer_code and len(customer_code) == 1:
                cust_code[prod.id][prod.product_id.id] = customer_code
            else:
                cust_code[prod.id][prod.product_id.id] = False

        logo = self.env.user.company_id.logo
        docargs = {
            'doc_ids': docids,
            'doc_model': 'mrp.production',
            'docs': production,
            'cust_code': cust_code,
            'line_qty': self.get_line_qty(production),
            'logo': logo,
        }
        return docargs


class ReportTagDebrand(models.AbstractModel):
    _name = 'report.report_tags.report_tag_debrand'
    _description = 'Report Tags Debrand'

    def get_line_qty(self, productions):
        line_qty = {}
        for doc in productions:
            if doc not in line_qty:
                line_qty[doc.id] = {doc.sale_line_id: doc.product_qty}
        return line_qty

    @api.multi
    def _get_report_values(self, docids, data=None):
        self.model = 'mrp.production'
        production = self.env[self.model].browse(docids)
        cust_code = {}
        for prod in production:
            cust_code[prod.id] = {}

            customer_code = self.env['product.product.customer'].search(
                [('product_id', '=', prod.product_id.id),
                 ('partner_id', '=', prod.partner_id.id)])

            if customer_code and len(customer_code) == 1:
                cust_code[prod.id][prod.product_id.id] = customer_code
            else:
                cust_code[prod.id][prod.product_id.id] = False

        logo = self.env.user.company_id.logo
        docargs = {
            'doc_ids': docids,
            'doc_model': self.model,
            'docs': production,
            'cust_code': cust_code,
            'line_qty': self.get_line_qty(production),
            'logo': logo,
        }
        return docargs
