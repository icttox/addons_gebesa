# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models

class ParticularReport(models.AbstractModel):
    _name = 'report.report_last_attachment.last_supplier_attachment'

    @api.multi
    def _get_report_values(self, docids, data=None):
        self.model = 'res.partner'
        docs = self.env[self.model].browse(docids)
        # for partner in docs:
        self.env.cr.execute("""
            SELECT
                rp.id,
                rp.name,
                ai.datas_fname,
                TO_CHAR(ai.create_date, 'DD/MM/YYYY hh:mm')
            FROM res_partner AS rp
            LEFT JOIN (SELECT MAX(create_date) AS create_date, res_id
                FROM ir_attachment WHERE res_model = 'res.partner' AND res_field IS NULL
                GROUP BY res_id) AS iar ON rp.id = iar.res_id
            LEFT JOIN ir_attachment AS ai ON iar.res_id = ai.res_id AND res_field IS NULL
                AND  iar.create_date = ai.create_date AND ai.res_model = 'res.partner'
            WHERE rp.supplier IS TRUE
                AND rp.active IS TRUE
                AND rp.company_id = (SELECT company_id FROM res_users WHERE id = %s)
            ORDER BY rp.name
        """ % self._uid)

        results = self.env.cr.fetchall()

        docargs = {
            'doc_ids': docids,
            'doc_model': self.model,
            'docs': docs,
            'results': results
        }

        return docargs
