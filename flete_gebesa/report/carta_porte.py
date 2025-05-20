# -*- coding: utf-8 -*-
# © <2018> <Aldo Nerio>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ParticularReport(models.AbstractModel):
    _name = 'report.flete_gebesa.report_carta_porte_travel'
    _description = 'descripcion pendiente'

    @api.multi
    def _get_report_values(self, docids, data=None):
        self.model = 'tms.waybill'
        #report_obj = self.env['report']
        #report = report_obj._get_report_from_name('flete_gebesa.report_carta_porte_travel')
        waybill_obj = self.env['tms.travel']
        waybill_var = waybill_obj.browse(docids)
        travel_arreglo = {}
        transportable_arreglo = {}
        # import pdb; pdb.set_trace()
        # contrato_var = contrato_obj.search([('employee_id', 'in', self.ids)], order="id desc", limit=1)
        self._cr.execute("""SELECT rp.name
                                FROM res_partner as rp
                                WHERE rp.id = %s""", ([waybill_var.partner_id.id]))
        if self._cr.rowcount:
            factura = self._cr.fetchone()[0]

        # import pdb; pdb.set_trace()
        docargs = {
            'doc_ids': docids,
            'docs': waybill_var,
            #'doc_model': report.model,
            'doc_model': self.model,
            'travel': travel_arreglo,
            'transportable': transportable_arreglo,
        }
        #return report_obj.render('flete_gebesa.report_carta_porte_travel', docargs)
        return docargs
