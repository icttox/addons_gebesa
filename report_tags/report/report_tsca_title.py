# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ParticularReport(models.AbstractModel):
    _name = 'report.report_tags.report_tsca'
    _description = 'Report Tags TSCA'

    @api.multi
    def _get_report_values(self, docids, data=None):
        self.model = 'mrp.production'
        production = self.env[self.model].browse(docids)
        logo = self.env.user.company_id.logo

        docargs = {
            'doc_ids': docids,
            'doc_model': self.model,
            'docs': production,
            'logo': logo,
        }

        return docargs
