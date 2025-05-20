# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ParticularReport(models.AbstractModel):
    _name = 'report.test_log.report_registro_pruebas'

    @api.multi
    def _get_report_values(self, docids, data=None):
        self.model = 'test.log'
        test_obj = self.env['test.log']
        test_var = test_obj.browse(docids)
        # import pdb; pdb.set_trace()

        docargs = {
            'doc_ids': test_var._ids,
            'docs': test_var,
            'doc_model': self.model,
        }
        return docargs
