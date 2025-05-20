# -*- coding: utf-8 -*-
# © <2018> <Aldo Nerio>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ParticularReport(models.AbstractModel):
    _name = 'report.purchase_order_global.report_order_global'

    @api.multi
    def _get_report_values(self, docids, data=None):
        self.model = 'res.partner'
        #report_obj = self.env['report']
        #report = report_obj._get_report_from_name('purchase_order_global.report_order_global')
        partner_obj = self.env['res.partner']
        partner_var = partner_obj.browse(docids)
        for doc in partner_var:
            self._cr.execute("""SELECT rp.name, pp.default_code, pol.name, pol.product_qty,
                                        pol.qty_received, pol.product_qty - pol.qty_received, po.date_order,
                                        po.name
                                FROM product_supplierinfo AS psi
                                    LEFT JOIN res_partner AS rp ON (rp.id = psi.name)
                                    LEFT JOIN product_template AS pt ON (pt.id = psi.product_tmpl_id)
                                    LEFT JOIN product_product AS pp ON (pp.product_tmpl_id = pt.id)
                                    LEFT JOIN purchase_order_line AS pol ON (pol.product_id = pp.id AND pol.partner_id = %s)
                                    LEFT JOIN purchase_order AS po ON (po.id = pol.order_id AND po.partner_id = %s AND po.state NOT IN ('cancel', 'draft'))
                                WHERE psi.name = %s
                                ORDER BY rp.name,pp.default_code""", (doc.id, doc.id, doc.id))

            if self._cr.rowcount:
                res = self._cr.fetchall()
        docargs = {
            'doc_ids': docids,
            'docs': partner_var,
            #'doc_model': report.model,
            'doc_model': self.model,
            'res': res,
        }
        #return report_obj.render('purchase_order_global.report_order_global', docargs)
        return docargs
