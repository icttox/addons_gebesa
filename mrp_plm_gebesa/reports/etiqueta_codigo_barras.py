# -*- coding: utf-8 -*-
# © <2018> <Aldo Nerio>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ParticularReport(models.AbstractModel):
    _name = 'report.mrp_plm_gebesa.report_codigo_barras'
    _description = 'descripcion pendiente'

    @api.multi
    def _get_report_values(self, docids, data=None):
        self.model = 'mrp.production'
        #report_obj = self.env['report']
        production_obj = self.env['mrp.production']
        #report = report_obj._get_report_from_name('mrp_plm_gebesa.report_codigo_barras')
        production = production_obj.browse(docids)
        logo = self.env.user.company_id.logo

        option_line = {}
        for prod in production:
            move = prod.move_prod_id.move_dest_id
            if move.location_dest_id.usage in ('customer', 'transit'):
                if move.location_dest_id.usage == 'transit':
                    move = move.move_dest_id.move_dest_id
                if move.procurement_id:
                    if move.procurement_id.sale_line_id:
                        option_line[prod.id] = (
                            move.procurement_id.sale_line_id.options)
                    else:
                        move = move.move_dest_id
                        if move.procurement_id:
                            if move.procurement_id.sale_line_id:
                                option_line[prod.id] = (
                                    move.procurement_id.sale_line_id.options)
                            else:
                                move = move.move_dest_id
                                if move.procurement_id:
                                    if move.procurement_id.sale_line_id:
                                        option_line[prod.id] = (
                                            move.procurement_id.sale_line_id.options)

        docargs = {
            'doc_ids': docids,
            #'doc_model': report.model,
            'doc_model': self.model,
            'docs': production,
            'logo': logo,
            'option_line': option_line,
        }
        #return report_obj.render('mrp_plm_gebesa.report_codigo_barras', docargs)
        return docargs
