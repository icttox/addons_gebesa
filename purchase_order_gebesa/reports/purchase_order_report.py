# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, models, exceptions


class ParticularReport(models.AbstractModel):
    _name = 'report.purchase_order_gebesa.report_purchase_order'
    _description = 'descripcion pendiente'

    @api.multi
    def _get_report_values(self, docids, data=None):
        self.model = 'purchase.order'
        docs = self.env[self.model].browse(docids)

        for doc in docs:
            for line in doc.order_line:

                sel = line.product_id.seller_ids.filtered(lambda seller: seller.name == doc.partner_id and seller.product_id == line.product_id)
                if not sel:
                    raise exceptions.UserError('Error: Favor de asignarle al producto este provedor: %s' % line.product_id.default_code)

        docargs = {
            'doc_ids': docids,
            'doc_model': self.model,
            'docs': docs,
        }
        return docargs
