# Copyright 2022, Marco Esquivel
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    id_microsip = fields.Integer(
        string='Microsip id',
    )

    type_overtime_hours = fields.Selection(
        [('01', 'Dobles'),
         ('02', 'Triples'),
         ('03', 'Simples')],
        string='Tipo de horas extras',
    )
