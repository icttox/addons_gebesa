# Copyright 2022, Marco Esquivel
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api


class HrJob(models.Model):
    _inherit = 'hr.job'

    currency_id = fields.Many2one(
        string="Currency",
        related='company_id.currency_id',
        readonly=True
    )

    wage = fields.Monetary(
        string='Salario',
        digits=(16, 2),
        required=True,
    )

    daily_salary = fields.Monetary(
        'Sueldo diario',
        digits=(16, 2),
        required=True,
    )

    assistance_award = fields.Float(
        string='Premio de Asistencia',
    )

    punctuality_award = fields.Float(
        string='Premio Puntualidad',
    )

    @api.multi
    def propagate_salaries(self):
        contracts = self.env['hr.contract'].search([
            ('job_id', '=', self.id),
            ('state', '!=', 'cancel'),
        ])
        for contract in contracts:
            contract.write({
                'wage': self.wage,
                'salario_diario': self.daily_salary,
                'premio_asistencia': self.assistance_award,
                'premio_puntualidad': self.punctuality_award
            })
