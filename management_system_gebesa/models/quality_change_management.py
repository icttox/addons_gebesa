# Copyright 2022, Marco Esquivel
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields, api


class QualityChangeManagement(models.Model):
    _name = 'quality.change.management'
    _inherit = ['message.post.show.all']
    _rec_name = 'folio'
    _description = 'descripcion pendiente'

    folio = fields.Char(
        string='Folio request',
    )

    date = fields.Date(
        string='Date request',
        default=fields.Date.context_today,
        required=True,
    )

    name_id = fields.Many2one(
        'hr.employee',
        string='Name applicate',
        required=True,
    )

    departament_id = fields.Many2one(
        'hr.department',
        string='Department',
        required=True,
    )

    exchange_rate = fields.Selection(
        [('changes_employee', 'Changes to employee opinions'),
         ('changes_satisfaction', 'Changes to satisfaction results'),
         ('changes_audit', 'Changes audit results'),
         ('risks', 'Risks'),
         ('opportunities', 'Opportunities'), ],
        string='Exchange rate',
        default='changes_employee',
        required=True,
    )

    description = fields.Char(
        string='Description of the change',
    )

    profits = fields.Char(
        string='Profits',
    )

    risks = field_name = fields.Char(
        string='Risks/consequences',
    )

    resources = fields.Char(
        string='Resources',
    )

    risk_matrix = fields.Boolean(
        string='Risk or opportunity matrix',
    )

    risk_matrix_name = fields.Char(
        string='Name/Document code',
    )

    risk_matrix_description = fields.Char(
        string='Description of the change',
    )

    risk_matrix_date = fields.Date(
        string='Date of realization',
    )

    indicator = fields.Boolean(
        string='Indicators',
    )

    indicator_name = fields.Char(
        string='Name/Document code',
    )

    indicator_description = fields.Char(
        string='Description of the change',
    )

    indicator_date = fields.Date(
        string='Date of realization',
    )

    procedures = fields.Boolean(
        string='Procedures, others',
    )

    procedures_name = fields.Char(
        string='Name/Document code',
    )

    procedures_description = fields.Char(
        string='Description of the change',
    )

    procedures_date = fields.Date(
        string='Date of realization',
    )

    activitis_ids = fields.One2many(
        'quality.change.management.lines',
        'change_lines_id',
    )

    check = fields.Many2one(
        'hr.employee',
        string='Check',
    )

    date_close = fields.Date(
        string='Date close',
        default=fields.Date.context_today,
    )

    status = fields.Selection(
        [('open', 'Abierto'),
         ('process', 'Proceso'),
         ('closed', 'Cerrado')],
        string='Status',
        default='open',
    )

    revised_id = fields.Many2one(
        'hr.employee',
        string='Revised',
    )

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.user.company_id,
    )

    @api.model
    def create(self, vals_list):
        vals_list['folio'] = self.env['ir.sequence'].next_by_code(
            'quality.change.management') or '/'
        return super().create(vals_list)
