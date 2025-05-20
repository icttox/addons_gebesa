# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ReportImmexGebesaReportTag1(models.AbstractModel):
    _name = 'report.immex_gebesa.report_tag1'
    _description = 'descripcion pendiente'

    @api.multi
    def _get_report_values(self, docids, data=None):
        self.model = 'input.product.wz'
        # report_obj = self.env['report']
        production_obj = self.env['input.product.wz']
        # report = report_obj._get_report_from_name('immex_gebesa.report_tag1')
        production = production_obj.browse(docids)

        docargs = {
            'doc_ids': docids,
            # 'doc_model': report.model,
            'doc_model': self.model,
            'docs': production,
        }
        # return report_obj.render('immex_gebesa.report_tag1', docargs)
        return docargs
