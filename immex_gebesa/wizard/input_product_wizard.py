# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, api, models


class InputProductWz(models.TransientModel):
    _name = 'input.product.wz'
    _description = 'descripcion pendiente'

    fecha_inicio = fields.Date(
        string='Fecha Inicio')

    fecha_final = fields.Date(
        string='Fecha Final')

    @api.multi
    def input_product_wz_m(self):
        ids = [self.id]
        ctx = dict(self.env.context or {},
                   active_ids=ids,
                   active_model=self._name)
        return{
            'type': 'ir.actions.report.xml',
            'report_name': 'immex_gebesa.report_tsca',
            'context': ctx,
        }
