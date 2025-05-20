# -*- coding: utf-8 -*-
# © <2018> <Aldo Nerio>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
# from dateutil.relativedelta import relativedelta


_logger = logging.getLogger(__name__)


class AccountYearClosing(models.Model):
    _name = 'account.year.closing'
    _inherit = ['message.post.show.all']
    _rec_name = 'description'
    _description = 'Account Year Closing'

    @api.model
    def _get_account_not_view_domain(self):
        ids = self.env.ref('account_account_parent.data_account_type_view').ids
        return [('user_type_id', '!=', ids)]

    @api.model
    def _get_previous_year(self):
        return fields.Date.from_string(fields.Date.today()).year - 1

    @api.model
    def _get_closing_journal(self):
        journal_id = self.env['account.journal'].search([
            ('active', '=', True),
            ('closing_year_journal', '=', True),
            ('type', '=', 'general'),
            ('company_id', '=', self.env.user.company_id.id)
        ], limit=1)
        return journal_id

    @api.model
    def _get_main_analytic(self):
        if self.env.user.company_id.main_analytic_id:
            return self.env.user.company_id.main_analytic_id

        analytic_id = self.env['account.analytic.account'].search([
            ('account_type', '=', 'normal'),
            ('parent_id', '=', False),
            ('use_salesorder', '=', False),
            ('company_id', '=', self.env.user.company_id.id)
        ], limit=1)
        return analytic_id

    description = fields.Char(
        string='Description',
        required=True,
    )

    state = fields.Selection(
        [('draft', 'Draft'),
         ('cancel', 'Cancelled'),
         ('done', 'Done')],
        string='Status',
        readonly=True,
        index=True,
        default='draft',
        copy=False
    )

    year = fields.Integer(
        string='Año',
        default=_get_previous_year,
        required=True,
    )

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env['res.company']._company_default_get(
            'account.year.closing')
    )

    date = fields.Date(
        default=fields.Date.today,
        string='Date',
        required=True,
        store=True,
    )

    account_acc_ids = fields.One2many(
        'account.account.value',
        'account_year_closing_id',
        string='Account',
    )

    date_start = fields.Date(
        string='Date Start',
    )

    date_end = fields.Date(
        string='Date End',
    )

    account_result_id = fields.Many2one(
        'account.account',
        string='Account Result',
        required=True,
        domain=_get_account_not_view_domain
    )
    journal_id = fields.Many2one(
        'account.journal',
        string='Journal',
        required=True,
        default=_get_closing_journal
    )
    move_id = fields.Many2one(
        'account.move',
        string='Journal Entry',
    )
    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        required=True,
        string='Analytic',
        default=_get_main_analytic
    )

    @api.onchange('year')
    def _onchange_year(self):
        try:
            self.date = str(self.year) + '-12-31'
        except ValueError:
            raise ValidationError(('Año no valido %s') % (str(self.year)))

    def get_data_line(self, move_ids):
        if len(move_ids) == 1:
            move_ids.append(0)
        self._cr.execute("""SELECT
                aa.id AS id_acount,
                aml.analytic_account_id,
                SUM(CASE WHEN aa.nature = 'A'
                    THEN aml.credit - aml.debit
                    ELSE aml.debit - aml.credit END /
                    COALESCE(rcr.rate,1)),
                aa.nature
            FROM account_account aa
            JOIN account_move_line aml ON aa.id  = aml.account_id
            JOIN account_move am ON aml.move_id = am.id
            LEFT JOIN res_currency_rate rcr ON aml.currency_id = rcr.currency_id
                AND am.date = CAST(rcr.name AS DATE) AND rcr.company_id = aml.company_id
                AND aml.journal_id IN (SELECT id FROM account_journal WHERE foreign_currency IS TRUE)
            WHERE aa.company_id = %s
                AND aa.id IN %s
                AND aml.date >= '%s'
                AND aml.date <= '%s'
                AND am.state != 'draft'
            GROUP BY aa.id, aml.analytic_account_id
            ORDER BY aa.id, aml.analytic_account_id
            """ % (
            self.company_id.id, tuple(move_ids),
            str(self.year) + '-01-02',
            str(self.year) + '-12-31'))
        return self._cr.fetchall()

    @api.multi
    def generate_policy(self):
        move_line_obj = self.env['account.move.line']

        for closing in self:
            _logger.error('account_year_closin line 168')
            closing.account_acc_ids.unlink()
            account_ids = self.env['account.account'].search([
                ('edores_type_id', '!=', False),
                ('company_id', '=', closing.company_id.id)
            ])

            account_debit = account_ids.filtered(
                lambda acc: acc.nature == 'A')
            self.env['account.account.value'].create({
                'account_year_closing_id': closing.id,
                'account_type': 'debe',
                'account_account_closing_id': [(6, 0, account_debit.ids)]
            })
            account_credit = account_ids.filtered(
                lambda acc: acc.nature == 'D')
            self.env['account.account.value'].create({
                'account_year_closing_id': closing.id,
                'account_type': 'haber',
                'account_account_closing_id': [(6, 0, account_credit.ids)]
            })
            _logger.error('account_year_closin line 189')
            account_debit = closing.mapped('account_acc_ids').filtered(
                lambda clos: clos.account_type == 'debe').mapped(
                'account_account_closing_id').mapped('id')
            account_credit = closing.mapped('account_acc_ids').filtered(
                lambda clos: clos.account_type == 'haber').mapped(
                'account_account_closing_id').mapped('id')
            if not account_debit and not account_credit:
                raise ValidationError(
                    _('No se registro ninguna cuenta'))
            for acc_deb in account_debit:
                if acc_deb in account_credit:
                    account = self.env['account.account'].browse([acc_deb])
                    raise ValidationError(
                        _('La cuenta %s : %s esta en el debe y en el haber') %
                        (account.code, account.name))
            _logger.error('account_year_closin line 205')
            # line_to_create = []
            diff = 0
            date_move = fields.Date.from_string(closing.date)
            # date_move += relativedelta(days=1)
            move_vals = {
                'ref': closing.description,
                # 'line_ids': line_to_create,
                'journal_id': closing.journal_id.id,
                'date': date_move,
            }
            move = self.env['account.move'].create(move_vals)
            _logger.error('account_year_closin line 217')
            if account_debit:
                debit_line = closing.get_data_line(account_debit)
                for line in debit_line:
                    if (round(line[2], 2) > 0 and line[3] == 'A') or \
                            (round(line[2], 2) < 0 and line[3] == 'D'):
                        move_line_obj.with_context({'check_move_validity': False}).create({
                            'name': closing.description,
                            'debit': abs(round(line[2], 2)),
                            'credit': 0.0,
                            'account_id': line[0],
                            'analytic_account_id': line[1],
                            'date': date_move,
                            'move_id': move.id,
                        })
                        diff += abs(round(line[2], 2))
                    if (round(line[2], 2) < 0 and line[3] == 'A') or \
                            (round(line[2], 2) > 0 and line[3] == 'D'):
                        move_line_obj.with_context({'check_move_validity': False}).create({
                            'name': closing.description,
                            'debit': 0,
                            'credit': abs(round(line[2], 2)),
                            'account_id': line[0],
                            'analytic_account_id': line[1],
                            'date': date_move,
                            'move_id': move.id,
                        })
                        diff -= abs(round(line[2], 2))
            _logger.error('account_year_closin line 245')
            if account_credit:
                credit_line = closing.get_data_line(account_credit)
                for line in credit_line:
                    if (round(line[2], 2) > 0 and line[3] == 'A') or \
                            (round(line[2], 2) < 0 and line[3] == 'D'):
                        move_line_obj.with_context({'check_move_validity': False}).create({
                            'name': closing.description,
                            'debit': abs(round(line[2], 2)),
                            'credit': 0.0,
                            'account_id': line[0],
                            'analytic_account_id': line[1],
                            'date': date_move,
                            'move_id': move.id,
                        })
                        diff += abs(round(line[2], 2))
                    if (round(line[2], 2) < 0 and line[3] == 'A') or \
                            (round(line[2], 2) > 0 and line[3] == 'D'):
                        move_line_obj.with_context({'check_move_validity': False}).create({
                            'name': closing.description,
                            'debit': 0,
                            'credit': abs(round(line[2], 2)),
                            'account_id': line[0],
                            'analytic_account_id': line[1],
                            'date': date_move,
                            'move_id': move.id,
                        })
                        diff -= abs(round(line[2], 2))
            _logger.error('account_year_closin line 273')
            if diff != 0.00:
                move_line_obj.create({
                    'name': closing.description,
                    'debit': abs(diff) if diff < 0 else 0.0,
                    'credit': diff if diff > 0 else 0.0,
                    'account_id': closing.account_result_id.id,
                    'analytic_account_id': closing.analytic_account_id.id,
                    'date': date_move,
                    'move_id': move.id,
                })
            _logger.error('account_year_closin line 284')
            closing.move_id = move.id
            closing.state = 'done'

    @api.multi
    def cancel_year_closing(self):
        for closing in self:
            if closing.move_id:
                closing.move_id.unlink()
            closing.state = 'cancel'

    @api.multi
    def draft_year_closing(self):
        for closing in self:
            closing.state = 'draft'
