# -*- coding: utf-8 -*-
# © <2018> <Aldo Nerio>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models
from odoo.exceptions import UserError


class ParticularReport(models.AbstractModel):
    _name = 'report.flete_gebesa.report_travel_expense'
    _description = 'descripcion pendiente'

    @api.multi
    def _get_report_values(self, docids, data=None):
        self.model = 'tms.travel'
        #report_obj = self.env['report']
        #report = report_obj._get_report_from_name(
        #    'flete_gebesa.report_travel_expense')
        travel_obj = self.env['tms.travel']
        travels = travel_obj.browse(docids)
        sum_products = {}
        caseta = False
        for travel in travels:
            if travel.tollstation_ids:
                for tollstation in travel.tollstation_ids:
                    caseta += tollstation.amount

            if travel.waybill_ids and len(travel.waybill_ids) > 1:
                raise UserError(('This travel has more than 1 waybill'))
            sum_products[travel.id] = {}
            for line in travel.advance_ids:
                if line.product_id.id not in sum_products[travel.id].keys():
                    sum_products[travel.id][line.product_id.id] = {
                        'product_id': line.product_id,
                        'amount': line.amount
                    }
                else:
                    sum_products[travel.id][line.product_id.id]['amount'] += line.amount
        docargs = {
            'doc_ids': docids,
            #'doc_model': report.model,
            'doc_model': self.model,
            'docs': travels,
            'sum_products': sum_products,
            'caseta': caseta,
        }
        #return report_obj.render('flete_gebesa.report_travel_expense', docargs)
        return docargs
