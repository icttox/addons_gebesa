# -*- coding: utf-8 -*-
# © <2018> <Aldo Nerio>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ParticularReport(models.AbstractModel):
    _name = 'report.informatica_gebesa.report_equipment_inventory'
    _description = 'descripcion pendiente'

    @api.multi
    def _get_report_values(self, docids, data=None):
        self.model = 'hr.employee'
        docs_obj = self.env[self.model].browse(docids)
        docargs = {
            'doc_ids': docids,
            'docs': docs_obj,
            'doc_model': self.model,
        }

        return docargs
