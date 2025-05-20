# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime
from odoo import fields, api, models


class InformeDescargosWizard(models.TransientModel):
    _name = 'informe.descargos.wizard'
    _description = 'descripcion pendiente'

    def _get_years(self):
        lst = []
        year = datetime.now().year
        year_init = 2017
        while year_init <= year:
            lst.append((year_init, year_init))
            year_init += 1
        return lst

    tipo_descargo = fields.Selection([
        ('A1', 'A1'),
        ('A3-B', 'A3-B'),
        ('A3-A', 'A3-A'),
        ('AJ', 'AJ'),
        ('BA', 'BA'),
        ('BB', 'BB'),
        ('BE', 'BE'),
        ('BP', 'BP'),
        ('BR', 'BR'),
        ('CFDI', 'CFDI'),
        ('CTM', 'CTM'),
        ('DES', 'DES'),
        ('DON', 'DON'),
        ('F3', 'F3'),
        ('F4', 'F4'),
        ('F5', 'F5'),
        ('H1', 'H1'),
        ('H8', 'H8'),
        ('I1', 'I1'),
        ('J3', 'J3'),
        ('J4', 'J4'),
        ('K1', 'K1'),
        ('RT', 'RT'),
        ('V1', 'V1'),
        ('V2', 'V2'),
        ('V3', 'V3'),
        ('V4', 'V4'),
        ('V5', 'V5'),
        ('V6', 'V6'),
        ('V7', 'V7'),
        ('V9', 'V9'),
        ('G9', 'G9')],
        string='Tipo de informe de descargo',
        required=True,)
    year = fields.Selection(_get_years, string='Año', required=True,)
    periodo = fields.Selection([
        ('01', 'Enero'),
        ('02', 'Febrero'),
        ('03', 'Marzo'),
        ('04', 'Abril'),
        ('05', 'Mayo'),
        ('06', 'Junio'),
        ('07', 'Julio'),
        ('08', 'Agosto'),
        ('09', 'Septiembre'),
        ('10', 'Octubre'),
        ('11', 'Noviembre'),
        ('12', 'Diciembre'),
    ], required=True,)

    @api.multi
    def print_corrections_init_inventory(self):
        return self.env.ref(
            'immex_gebesa.immex_informe_descargos').report_action(
            self)
