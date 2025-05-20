# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ParticularReport(models.AbstractModel):
    _name = 'report.contrarecibo_gebesa.report_contrarecibo'

    @api.multi
    def _get_report_values(self, docids, data=None):
        self.model = 'contrarecibo'
        # report_obj = self.env['report']
        contrarecibo_obj = self.env['contrarecibo']
        # report = report_obj._get_report_from_name(
        #     'contrarecibo_gebesa.report_contrarecibo')
        contrarecibo = contrarecibo_obj.browse(docids)
        logo = self.env.user.company_id.logo
        docargs = {
            'doc_ids': docids,
            # 'doc_model': report.model,
            'doc_model': self.model,
            'docs': contrarecibo,
            'logo': logo,
            'data': data,
        }
        # return report_obj.render('contrarecibo_gebesa.report_contrarecibo',
        #                         docargs)
        return docargs
