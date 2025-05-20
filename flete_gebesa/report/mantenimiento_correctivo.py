# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ParticularReport(models.AbstractModel):
    _name = 'report.flete_gebesa.report_mantenimiento_correctivo'
    _description = 'descripcion pendiente'

    @api.multi
    def _get_report_values(self, docids, data=None):
        self.model = 'tms.travel'
        #report_obj = self.env['report']
        #report = report_obj._get_report_from_name('flete_gebesa.report_mantenimiento_correctivo')
        travel_obj = self.env['tms.travel']
        user_obj = self.env['res.users']
        travel_var = travel_obj.browse(docids)
        # import pdb; pdb.set_trace()
        user_var = user_obj.browse(self._uid)
        nombre_usuario = False
        nombre_usuario = user_var.partner_id.name
        travel = {}
        docargs = {
            'doc_ids': docids,
            'docs': travel_var,
            'nombre_usuario': nombre_usuario,
            #'doc_model': report.model,
            'doc_model': self.model,
            'travel': travel,
        }
        #return report_obj.render('flete_gebesa.report_mantenimiento_correctivo', docargs)
        return docargs
