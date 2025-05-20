# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ParticularReport(models.AbstractModel):
    _name = 'report.report_invoice_cfdi32.report_cfdi'

    @api.multi
    def _get_report_values(self, docids, data=None):
        self.model = 'account.invoice'
        #report_obj = self.env['report']
        invoice_obj = self.env['account.invoice']
        bom_obj = self.env['mrp.bom']
        boms = {}

        #report = report_obj._get_report_from_name(
        #    'report_invoice_cfdi32.report_cfdi')
        invoice = invoice_obj.browse(docids)

        for inv in invoice:
            for line in invoice.invoice_line_ids:
                if line.product_id.id not in boms.keys():
                    bom = bom_obj.search([
                        ('product_id', '=', line.product_id.id)])
                    if bom and bom.type == 'phantom':
                        boms[line.product_id.id] = bom

        docargs = {
            'doc_ids': docids,
            #'doc_model': report.model,
            'doc_model': self.model,
            'docs': invoice,
            'bom': boms
        }
        #return report_obj.render('report_invoice_cfdi32.report_cfdi', docargs)
        return docargs
