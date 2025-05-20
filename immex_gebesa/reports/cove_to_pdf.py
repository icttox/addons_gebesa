# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ReportCoveToPdf(models.AbstractModel):
    _name = 'report.immex_gebesa.report_cove_to_pdf'
    _description = 'descripcion pendiente'

    @api.model
    def search_rfc(self, data):
        partner = self.env['res.partner'].search([
            ('vat', '=', data)], order='id', limit=1)
        if partner:
            return partner.name
        return ''

    @api.model
    def search_country(self, data):
        country = self.env['res.country'].search([
            ('fiscal_code', '=', data)], limit=1)
        if country:
            return country.name
        return data

    @api.multi
    def _get_report_values(self, docids, data=None):
        self.model = 'l10n.mx.immex.pedimento'
        pedimentos = self.env[self.model].browse(docids)

        docargs = {
            'doc_ids': docids,
            'doc_model': self.model,
            'docs': pedimentos,
            'search_rfc': self.search_rfc,
            'search_country': self.search_country,
            'data': data
        }
        return docargs
