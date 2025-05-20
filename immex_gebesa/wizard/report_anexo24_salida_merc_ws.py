# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, api, models


class ReportAnexo24SalidaMercWs(models.TransientModel):
    _name = 'report.anexo24.salida.merc.ws'
    _description = 'descripcion pendiente'

    fecha_inicio = fields.Date(
        string='Fecha Inicio')

    fecha_final = fields.Date(
        string='Fecha Final')

    @api.multi
    def get_report_salida_mercancia(self):
        return self.env.ref(
            'immex_gebesa.salida_mercancia_anexo24').report_action(self)
