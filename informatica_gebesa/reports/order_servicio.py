# -*- coding: utf-8 -*-
# © <2018> <Aldo Nerio>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ParticularReport(models.AbstractModel):
    _name = 'report.informatica_gebesa.report_order_servicio'
    _description = 'descripcion pendiente'

    @api.multi
    def _get_report_values(self, docids, data=None):
        self.model = 'maintenance.equipment'
        #report_obj = self.env['report']
        #report = report_obj._get_report_from_name('informatica_gebesa.report_order_servicio')
        docs_obj = self.env['maintenance.request'].sudo().browse(docids)
        empleado = {}
        for doc in docs_obj:
            empleado[doc.id] = []
            empleado[doc.id].append({'usuario': doc.employee_id.name,
                                     'departamento': doc.employee_id.department_id.name,
                                     'fecha': doc.request_date,
                                     'note': doc.description,
                                     'categoria': doc.category_id.name
                                     })
        docargs = {
            'doc_ids': docids,
            'docs': docs_obj,
            #'doc_model': report.model,
            'doc_model': self.model
        }
        #return report_obj.render('informatica_gebesa.report_order_servicio', docargs)
        return docargs
