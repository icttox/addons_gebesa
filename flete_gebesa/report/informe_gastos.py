# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ParticularReport(models.AbstractModel):
    _name = 'report.flete_gebesa.report_informe_gastos'
    _description = 'descripcion pendiente'

    @api.multi
    def _get_report_values(self, docids, data=None):
        self.model = 'tms.travel'
        #report_obj = self.env['report']
        #report = report_obj._get_report_from_name('flete_gebesa.report_informe_gastos')
        travel_obj = self.env['tms.travel']
        travel_var = travel_obj.browse(docids)
        # import pdb; pdb.set_trace()
        # for doc in travel_var:
        docargs = {
            'doc_ids': travel_var._ids,
            'docs': travel_var,
            #'doc_model': report.model,
            'doc_model': self.model,
        }
        #return report_obj.render('flete_gebesa.report_informe_gastos', docargs)
        return docargs
