# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class InputReport(models.AbstractModel):
    _name = 'report.immex_gebesa.report_corrections_initial_inventory'
    _description = 'descripcion pendiente'

    @api.multi
    def _get_report_values(self, docids, data=None):
        self.model = 'corrections.initial.inventory.wizard'
        corrections_obj = self.env['corrections.initial.inventory.wizard']
        corrections = corrections_obj.browse(docids)

        partidas = self.env['l10n.mx.immex.partida'].search([
            ('amount', '>', 0.00),
            ('clave_documento', 'in', ['IN', 'V1', 'AF'])])

        docargs = {
            'doc_ids': docids,
            'doc_model': self.model,
            'docs': corrections,
            'partidas': partidas,
            'data': data,
        }
        return docargs
