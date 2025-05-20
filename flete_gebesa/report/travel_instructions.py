# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ParticularReport(models.AbstractModel):
    _name = 'report.flete_gebesa.report_travel_instructions'
    _description = 'descripcion pendiente'

    @api.multi
    def _get_report_values(self, docids, data=None):
        self.model = 'tms.travel'
        #report_obj = self.env['report']
        #report = report_obj._get_report_from_name('flete_gebesa.report_travel_instructions')
        travel_obj = self.env['tms.travel']
        travel_var = travel_obj.browse(docids)
        docs = []
        docs2 = {}
        partn = []
        orden = []
        fac = []
        facturas = []
        for doc in travel_var:
            # for shipment in doc.shipment_id:
            #	for order in shipment.sale_ids:
            self._cr.execute("""SELECT  rp.name
                                FROM mrp_shipment as ms
                                    JOIN mrp_shipment_sale as mss ON(mss.shipment_id = ms.id)
                                    JOIN res_partner as rp ON (rp.id = mss.partner_id)
                                WHERE ms.id = %s
                                GROUP BY rp.name """, ([doc.shipment_id.id]))
            # import pdb; pdb.set_trace()
            if self._cr.rowcount:
                resultado = self._cr.fetchall()
                for x in resultado:
                    for i in x:
                        if i not in partn:
                            partn.append(i)
            # SEGUNDA CONSULTA PARA TRAER LAS ORDENES
            self._cr.execute("""SELECT string_agg(so.name,',')
                                FROM mrp_shipment as ms
                                    JOIN mrp_shipment_sale as mss ON(mss.shipment_id = ms.id)
                                    JOIN sale_order as so ON (so.id = mss.sale_id)
                                    JOIN res_partner as rp ON (rp.id = mss.partner_id)
                                WHERE ms.id = %s
                                GROUP BY rp.name """, ([doc.shipment_id.id]))
            # import pdb; pdb.set_trace()
            if self._cr.rowcount:
                resultado2 = self._cr.fetchall()
                for res in resultado2:
                    for j in res:
                        if j not in orden:
                            orden.append(j)
            # TERCERA CONSULTA SE TRAE LAS FACURAS
            self._cr.execute("""SELECT string_agg(CAST(ai.travel_id AS TEXT),',')
                                FROM mrp_shipment as ms
                                    JOIN mrp_shipment_sale as mss ON(mss.shipment_id = ms.id)
                                    JOIN res_partner as rp ON (rp.id = mss.partner_id)
                                    JOIN account_invoice as ai ON (ai.partner_id IN (rp.id) AND ai.travel_id = %s)
                                WHERE ms.id = %s
                                GROUP BY rp.name """, (doc.id, doc.shipment_id.id))
            # import pdb; pdb.set_trace()
            if self._cr.rowcount:
                resultado3 = self._cr.fetchall()
                for res2 in resultado3:
                    for k in res2:
                        if k not in facturas:
                            facturas.append(k)
            # TERCERA CONSULTA SE TRAE LAS FACURAS
            self._cr.execute("""SELECT string_agg(CAST(ai.travel_id AS TEXT),',')
                                FROM account_invoice as ai
                                WHERE ai.travel_id = %s """, ([doc.id]))
            if self._cr.rowcount:
                resultado4 = self._cr.fetchall()
                for res3 in resultado4:
                    for m in res3:
                        if m not in fac:
                            fac.append(m)
            index = doc.id
            # docs.append(index)
            docs2[index] = []
            docs2[index].append({'a': partn})
            docs2[index].append({'b': partn})
            docs2[index].append({'c': orden})
            # docs[doc.id].append({'b': orden})

            docs.append({
                'ordenes': partn,
                'fecha': doc.date,
                'contador': 1,
                # 'operador': doc.employee_id.name_related,
                # 'celular': doc.employee_id.work_phone,
                # 'caja': doc.unit_id.load_capacity,
                # 'placas': doc.unit_id.license_plate,
                # 'destino': doc.route_id.name,
                # 'kms': doc.route_id.distance,
                # 'fletera': doc.user_id.company_id.name,
                # 'fecha_sal': doc.date_start,
                # 'embarque': doc.shipment_id.folio,

                # 'folio': doc.folio,
                # 'products': products,
                # 'cut_line': cut_line,
                # 'cut_detail': cut_detail,
            })
        # import pdb; pdb.set_trace()
        docargs = {
            'doc_ids': docids,
            #'doc_model': report.model,
            'doc_model': self.model,
            'docs': docs,
            'trav': travel_var,
            'part': partn,
            'sale': orden,
            'docs2': docs2,
            'fact': facturas,
        }
        # return report_obj.render(
        #     'flete_gebesa.report_travel_instructions',
        #     docargs)
        return docargs
