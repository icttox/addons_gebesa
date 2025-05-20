# -*- coding: utf-8 -*-
# © <2018> <Aldo Nerio>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ParticularReport(models.AbstractModel):
    _name = 'report.rh_gebesa.report_ingreso_personal'
    _description = 'descripcion pendiente'

    @api.multi
    def _get_report_values(self, docids, data=None):
        self.model = 'hr.employee'
        empleado_obj = self.env['hr.employee']
        empleado_var = empleado_obj.browse(docids)

        docargs = {
            'doc_ids': docids,
            'docs': empleado_var,
            'doc_model': self.model,
            'data': data,
        }
        return docargs
