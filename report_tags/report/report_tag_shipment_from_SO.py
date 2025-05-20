# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ParticularReport(models.AbstractModel):
    _name = 'report.report_tags.report_so_shipment_tag'
    _description = 'Report Tags SO Shipment'

    @api.multi
    def _get_report_values(self, docids, data=None):
        self.model = 'sale.order'
        saleorder = self.env[self.model].browse(docids)
        pag_tot = {}
        # first_tag = {}
        # last_tag = {}
        # logo = self.env.user.company_id.logo
        for order in saleorder:
            pages = 0
            # first_tag[order.id] = order.counter_tag + 1
            # order.counter_tag += 700
            # last_tag[order.id] = order.counter_tag
            for lines in order.order_line:
                pages += int(lines.product_uom_qty)
            # if order.counter_tag > pages:
                # order.counter_tag = 0
            pag_tot[order.id] = pages
        docargs = {
            'doc_ids': docids,
            'doc_model': self.model,
            'docs': saleorder,
            # 'logo': logo,
            'pag_tot': pag_tot,
            # 'first_tag': first_tag,
            # 'last_tag': last_tag,
        }
        return docargs


class ReportSoShipmentTagDebranded(models.AbstractModel):
    _name = 'report.report_tags.report_so_shipment_tag_debranded'
    _description = 'descripcion pendiente'

    @api.multi
    def _get_report_values(self, docids, data=None):
        self.model = 'sale.order'
        saleorder = self.env[self.model].browse(docids)
        pag_tot = {}
        for order in saleorder:
            pages = 0
            for lines in order.order_line:
                pages += int(lines.product_uom_qty)
            pag_tot[order.id] = pages
        docargs = {
            'doc_ids': docids,
            'doc_model': self.model,
            'docs': saleorder,
            'pag_tot': pag_tot,
        }
        return docargs
