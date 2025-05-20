# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ParticularReport(models.AbstractModel):
    _name = 'report.report_tags.report_shipment_tag_2'
    _description = 'Report Tags Shipment 2'

    @api.multi
    def _get_report_values(self, docids, data=None):
        self.model = 'mrp.shipment'
        pag_tot = {}
        shipment = self.env[self.model].browse(docids)
        logo = self.env.user.company_id.logo
        for ship in shipment:
            pages = 0
            for lines in ship.line_ids:
                pages += int(lines.quantity_shipped)
            pag_tot[ship.id] = pages
        docargs = {
            'doc_ids': docids,
            'doc_model': self.model,
            'docs': shipment,
            'logo': logo,
            'pag_tot': pag_tot,
        }
        return docargs
