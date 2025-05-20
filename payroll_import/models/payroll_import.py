# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError


class PayrollImport(models.Model):
    _name = 'payroll.import'
    _description = 'Payroll import'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _get_invoice_line(self):
        res = {}
        for line in self.lines_ids:
            res[line.id] = True
        return res.keys()

    name = fields.Char(
        string='Code',
        size=64,
        state={'done': [('readonly', True)]},
    )
    date = fields.Date(
        string='Date',
        default=fields.Date.today,
        state={'done': [('readonly', True)]},
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.user.company_id,
        state={'done': [('readonly', True)]},
    )
    journal_id = fields.Many2one(
        'account.journal',
        string='Journal',
        state={'done': [('readonly', True)]},
    )
    move_id = fields.Many2one(
        'account.move',
        string='Journal Entry',
    )
    debit = fields.Float(
        string='Debit',
        compute='compute_totals',
        digits=dp.get_precision('Account'),
        track_visibility='always',
        store=True,
        multi='all',
    )
    credit = fields.Float(
        string='Credit',
        compute='compute_totals',
        digits=dp.get_precision('Account'),
        track_visibility='always',
        store=True,
        multi='all',
    )
    state = fields.Selection(
        [('draft', 'Draft'),
         ('done', 'Done')],
        string='State',
        default='draft',
    )
    lines_ids = fields.One2many(
        'payroll.import.line',
        'payroll_id',
        string='Payroll lines',
    )

    @api.depends('lines_ids.debit', 'lines_ids.credit')
    def compute_totals(self):
        for payroll in self:
            for line in payroll.lines_ids:
                payroll.debit += line.debit
                payroll.credit += line.credit

    @api.multi
    def action_done(self):
        move_obj = self.env['account.move']
        move_line_obj = self.env['account.move.line']

        for payroll in self:
            if payroll.debit != payroll.credit:
                raise UserError('Cannot create unbalanced payroll.')

            vals = {
                'journal_id': payroll.journal_id.id,
                'date': payroll.date,
                'ref': payroll.name,
                'company_id': payroll.company_id.id
            }

            move_id = move_obj.create(vals)

            for line in payroll.lines_ids:
                line_vals = {
                    'move_id': move_id.id,
                    'journal_id': payroll.journal_id.id,
                    'date': payroll.date,
                    'debit': line.debit > 0 and line.debit or 0.0,
                    'credit': line.credit > 0 and line.credit or 0.0,
                    'name': line.description,
                    'account_id': line.account_id.id,
                    'analytic_account_id': line.analytic_account_id.id,
                }
                move_line_obj.with_context(
                    {'check_move_validity': False}).create(line_vals)

            move_id.post()
            payroll.move_id = move_id.id
            payroll.state = 'done'

        return


class PayrollImportLine(models.Model):
    _name = 'payroll.import.line'
    _description = 'Payroll import line'

    payroll_id = fields.Many2one(
        'payroll.import',
        string='Payroll',
        ondelete='cascade',
        index=2,
        required=True,
    )
    account_id = fields.Many2one(
        'account.account',
        string='Account',
    )
    debit = fields.Float(
        string='Debit',
        digits=dp.get_precision('Account'),
    )
    credit = fields.Float(
        string='Credit',
        digits=dp.get_precision('Account'),
    )
    description = fields.Char(
        string='Description',
        size=256,
    )
    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='Analytic',
    )
