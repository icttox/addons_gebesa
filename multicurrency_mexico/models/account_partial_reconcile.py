# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from collections import OrderedDict
from datetime import date
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountPartialReconcile(models.Model):
    _inherit = 'account.partial.reconcile'

    partial_exchange_move_id = fields.Many2one('account.move')

    def create_exchange_rate_entry(self, aml_to_fix, move):
        line_to_reconcile, partial_rec = super(
            AccountPartialReconcile, self).create_exchange_rate_entry(
            aml_to_fix, move)

        # move.date = max(self.credit_move_id.date, self.debit_move_id.date)
        for aml in aml_to_fix:
            move.move_exchange_id = aml.move_id.id

        return line_to_reconcile, partial_rec

    @api.model
    def create(self, vals):
        res = super(AccountPartialReconcile, self).create(vals)
        if self._context.get('skip_full_reconcile_check'):
            # when running the manual reconciliation wizard, don't check the
            # partials separately for full reconciliation or exchange rate
            # because it is handled manually after the whole processing
            return res
        # check if the reconcilation is full first,
        # gather all journal items involved in the reconciliation just created
        partial_rec_set = OrderedDict.fromkeys([x for x in res])
        maxdate = None
        aml_to_balance = None
        currency_company = self.env.user.company_id.currency_id
        currency = list(partial_rec_set)[0].currency_id
        if currency_company != currency:
            for partial_rec in partial_rec_set:
                if partial_rec.currency_id != currency:
                    # no exchange rate entry will be created
                    continue

                if partial_rec.amount_currency == 0:
                    continue

                debit_move = partial_rec.debit_move_id
                credit_move = partial_rec.credit_move_id
                maxdate = max(debit_move.date, credit_move.date)

                if not debit_move.amount_residual_currency and not credit_move.amount_residual_currency:
                    continue

                if debit_move.currency_id and debit_move.currency_id == currency:
                    debit_amount_currency = abs(debit_move.amount_currency)
                elif partial_rec.currency_id and partial_rec.currency_id == currency:
                    # debit_amount_currency = abs(debit_move.company_id.currency_id.with_context(
                    #     date=debit_move.date).compute(debit_move.balance, partial_rec.currency_id))
                    debit_amount_currency = abs(debit_move.company_id.currency_id._convert(
                        debit_move.balance, partial_rec.currency_id, partial_rec.company_id, debit_move.date))

                if credit_move.currency_id and credit_move.currency_id == currency:
                    credit_amount_currency = abs(credit_move.amount_currency)
                elif partial_rec.currency_id and partial_rec.currency_id == currency:
                    # credit_amount_currency = abs(credit_move.company_id.currency_id.with_context(
                    #     date=credit_move.date).compute(credit_move.balance, partial_rec.currency_id))
                    credit_amount_currency = abs(credit_move.company_id.currency_id._convert(
                        credit_move.balance, partial_rec.currency_id, partial_rec.company_id, credit_move.date))

                if debit_amount_currency > credit_amount_currency:
                    rate = round(abs(debit_move.debit / debit_amount_currency), 6)
                    credit = credit_move.credit
                    debit = credit_amount_currency * rate
                    diff = debit - credit
                    if abs(diff) > 0.01:
                        if diff > 0:
                            aml_to_balance = debit_move
                        elif diff < 0:
                            aml_to_balance = credit_move
                            partial_rec.amount += diff
                else:
                    rate = round(abs(credit_move.credit / credit_amount_currency), 6)
                    credit = debit_amount_currency * rate
                    debit = debit_move.debit
                    diff = debit - credit
                    if abs(diff) > 0.01:
                        if diff > 0:
                            aml_to_balance = debit_move
                            partial_rec.amount -= diff
                        elif diff < 0:
                            aml_to_balance = credit_move

                if not aml_to_balance:
                    continue

                aml_id, partial_rec_id, move_exchange = partial_rec.create_exchange_rate_entry_partial(
                    aml_to_balance, diff, 0.00, currency, maxdate)

                res.partial_exchange_move_id = move_exchange
        return res

    def create_exchange_rate_entry_partial(self, aml_to_fix, amount_diff, diff_in_currency, currency, move_date):
        """ Automatically create a journal entry to book the exchange rate difference.
            That new journal entry is made in the company `currency_exchange_journal_id` and one of its journal
            items is matched with the other lines to balance the full reconciliation.
        """
        for rec in self:
            if not rec.company_id.currency_exchange_journal_id:
                raise UserError(_("You should configure the 'Exchange Rate Journal' in the accounting settings, to manage automatically the booking of accounting entries related to differences between exchange rates."))
            if not rec.company_id.income_currency_exchange_account_id.id:
                raise UserError(_("You should configure the 'Gain Exchange Rate Account' in the accounting settings, to manage automatically the booking of accounting entries related to differences between exchange rates."))
            if not rec.company_id.expense_currency_exchange_account_id.id:
                raise UserError(_("You should configure the 'Loss Exchange Rate Account' in the accounting settings, to manage automatically the booking of accounting entries related to differences between exchange rates."))
            move_vals = {'journal_id': rec.company_id.currency_exchange_journal_id.id, 'rate_diff_partial_rec_id': rec.id}

            # The move date should be the maximum date between payment and invoice (in case
            # of payment in advance). However, we should make sure the move date is not
            # recorded after the end of year closing.
            if rec.company_id.fiscalyear_lock_date:
                if move_date > rec.company_id.fiscalyear_lock_date:
                    move_vals['date'] = move_date
            else:
                move_vals['date'] = move_date
            move = rec.env['account.move'].create(move_vals)
            amount_diff = rec.company_id.currency_id.round(amount_diff)
            diff_in_currency = currency.round(diff_in_currency)
            line_to_reconcile = rec.env['account.move.line'].with_context(check_move_validity=False).create({
                'name': _('Currency exchange rate difference'),
                'debit': amount_diff < 0 and -amount_diff or 0.0,
                'credit': amount_diff > 0 and amount_diff or 0.0,
                'account_id': rec.debit_move_id.account_id.id,
                'move_id': move.id,
                'currency_id': currency.id,
                'amount_currency': -diff_in_currency,
                'partner_id': rec.debit_move_id.partner_id.id,
            })
            rec.env['account.move.line'].create({
                'name': _('Currency exchange rate difference'),
                'debit': amount_diff > 0 and amount_diff or 0.0,
                'credit': amount_diff < 0 and -amount_diff or 0.0,
                'account_id': amount_diff > 0 and rec.company_id.currency_exchange_journal_id.default_debit_account_id.id or rec.company_id.currency_exchange_journal_id.default_credit_account_id.id,
                'move_id': move.id,
                'currency_id': currency.id,
                'amount_currency': diff_in_currency,
                'partner_id': rec.debit_move_id.partner_id.id,
            })
            for aml in aml_to_fix:
                # DO NOT FORWARDPORT! ONLY FOR v9
                partial_rec = rec.env['account.partial.reconcile'].with_context(cash_basis=False).create({
                    'debit_move_id': aml.credit and line_to_reconcile.id or aml.id,
                    'credit_move_id': aml.debit and line_to_reconcile.id or aml.id,
                    'amount': abs(amount_diff),
                    'amount_currency': abs(diff_in_currency),
                    'currency_id': currency.id,
                })
                move.move_exchange_id = aml.move_id.id
            move.post()
        return line_to_reconcile.id, partial_rec.id, move.id

    @api.multi
    def unlink(self):
        rec_move_ids = self.env['account.move']
        for apr in self:
            if apr.exists() and apr.partial_exchange_move_id:
                rec_move_ids += apr.partial_exchange_move_id
                apr.partial_exchange_move_id = False
        res = super(AccountPartialReconcile, self).unlink()
        for to_reverse in rec_move_ids:
            # reverse the exchange rate entry after de-referencing it to avoid looping
            # (reversing will cause a nested attempt to drop the full reconciliation)
            if to_reverse.date > (to_reverse.company_id.period_lock_date or date.min):
                to_reverse.reverse_moves(date=to_reverse.date)
            else:
                to_reverse.reverse_moves()
        return res
