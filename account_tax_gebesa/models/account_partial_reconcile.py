# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from collections import defaultdict
from odoo import models
from odoo.tools import float_is_zero


class AccountPartialReconcile(models.Model):
    _inherit = 'account.partial.reconcile'

    def _get_tax_cash_basis_base_common_vals(self, key, new_move):
        res = super()._get_tax_cash_basis_base_common_vals(key, new_move)
        res['diot'] = True
        return res

    def _get_amount_tax_cash_basis(self, amount, line):
        if (self.env.user.company_id.country_id != self.env.ref('base.mx') or
                not line.currency_id or not self.debit_move_id.currency_id or
                not self.credit_move_id.currency_id):
            return (super()._get_amount_tax_cash_basis(amount, line))

        aml_obj = self.env['account.move.line']
        aml_ids = (self.debit_move_id | self.credit_move_id).ids
        # Use the payment date to compute currency conversion. When reconciling
        # an invoice and a credit note - we will use the greatest date of them.
        domain = [('id', 'in', aml_ids), ('invoice_id', '!=', False),
                  ('payment_id', '!=', False)]
        move_date = aml_obj.search(domain, limit=1, order="date desc").date
        if not move_date:
            domain.pop()
            move_date = aml_obj.search(domain, limit=1, order="date desc").date
        if not move_date:
            return (super()._get_amount_tax_cash_basis(amount, line))
        return (
            line.amount_currency and line.balance and
            # line.currency_id.with_context(date=move_date).compute(
            #     line.amount_currency * amount / line.balance,
            #     line.company_id.currency_id) or 0.0)
            line.currency_id._convert(
                line.amount_currency * amount / line.balance,
                line.company_id.currency_id,
                line.company_id,
                move_date) or 0.0)

    def create_tax_cash_basis_entry(self, percentage_before_rec):
        self.ensure_one()
        move_date = max(self.debit_move_id.date, self.credit_move_id.date)
        cash_basis_amount_dict = defaultdict(float)
        cash_basis_amount_currency_dict = defaultdict(float)
        newly_created_move = self.env['account.move']
        if self.credit_move_id.move_id:
            move = self.credit_move_id.move_id
            invoice = self.env['account.invoice'].search([
                ('move_id', '=', move.id)])
            if (invoice and invoice.type == 'out_refund') or move.manual:
                return
        if self.debit_move_id.move_id:
            move = self.debit_move_id.move_id
            invoice = self.env['account.invoice'].search([
                ('move_id', '=', move.id)])
            if (invoice and invoice.type == 'in_refund') or move.manual:
                return
        if self._context.get('create_tax', True):
            move_untax_id = False
            with self.env.norecompute():
                for move in (self.debit_move_id.move_id, self.credit_move_id.move_id):
                    move_untax = True
                    for line in move.line_ids:
                        # TOCHECK: normal and cash basis taxes shoudn't be mixed
                        # together (on the same invoice line for example) as it will
                        # create reporting issues. Not sure of the behavior to
                        # implement in that case, though.
                        if not line.tax_exigible:
                            percentage_before = percentage_before_rec[move.id]
                            percentage_after = line._get_matched_percentage()[move.id]
                            # amount is the current cash_basis amount minus the
                            # one before the reconciliation
                            amount = line.balance * percentage_after - line.balance * percentage_before
                            rounded_amt = self._get_amount_tax_cash_basis(amount, line)
                            if float_is_zero(rounded_amt, precision_rounding=line.company_id.currency_id.rounding):
                                continue
                            if line.tax_line_id and line.tax_line_id.tax_exigibility == 'on_payment':
                                move_untax = False
                                if not newly_created_move:
                                    # move_untaxed_id
                                    newly_created_move = self.with_context(
                                        default_move_untaxed_id=line.move_id.id)._create_tax_basis_move()
                                    if move_date > (self.company_id.period_lock_date or '0000-00-00') and newly_created_move.date != move_date:
                                        # The move date should be the maximum date between payment and
                                        # invoice (in case of payment in advance). However, we should
                                        # make sure the move date is not recorded before the period
                                        # lock date as the tax statement for this period is probably
                                        # already sent to the estate.
                                        newly_created_move.write({'date': move_date})
                                # create cash basis entry for the tax line
                                to_clear_aml = self.env['account.move.line'].with_context(check_move_validity=False).create({
                                    'name': line.move_id.name,
                                    'debit': abs(rounded_amt) if rounded_amt < 0 else 0.0,
                                    'credit': rounded_amt if rounded_amt > 0 else 0.0,
                                    'account_id': line.account_id.id,
                                    # DO NOT FORWARD-PORT!!! ONLY FOR v11
                                    'analytic_account_id': line.analytic_account_id.id,
                                    'analytic_tag_ids': line.analytic_tag_ids.ids,
                                    'tax_exigible': True,
                                    'amount_currency': line.amount_currency and line.currency_id.round(-line.amount_currency * amount / line.balance) or 0.0,
                                    'currency_id': line.currency_id.id,
                                    'move_id': newly_created_move.id,
                                    'partner_id': line.partner_id.id,
                                })
                                # Group by cash basis account and tax
                                self.env['account.move.line'].with_context(check_move_validity=False).create({
                                    'name': line.name,
                                    'debit': rounded_amt if rounded_amt > 0 else 0.0,
                                    'credit': abs(rounded_amt) if rounded_amt < 0 else 0.0,
                                    'account_id': line.tax_line_id.cash_basis_account_id.id,
                                    # DO NOT FORWARD-PORT!!! ONLY FOR v11
                                    'analytic_account_id': line.analytic_account_id.id,
                                    'analytic_tag_ids': line.analytic_tag_ids.ids,
                                    'tax_line_id': line.tax_line_id.id,
                                    'tax_exigible': True,
                                    'amount_currency': line.amount_currency and line.currency_id.round(line.amount_currency * amount / line.balance) or 0.0,
                                    'currency_id': line.currency_id.id,
                                    'move_id': newly_created_move.id,
                                    'partner_id': line.partner_id.id,
                                })
                                if line.account_id.reconcile:
                                    # setting the account to allow reconciliation
                                    # will help to fix rounding errors
                                    to_clear_aml |= line
                                    to_clear_aml.reconcile()

                            if any([tax.tax_exigibility == 'on_payment' for tax in line.tax_ids]):
                                # create cash basis entry for the base
                                for tax in line.tax_ids.filtered(lambda t: t.tax_exigibility == 'on_payment'):
                                    # We want to group base lines as much as
                                    # possible to avoid creating too many of them.
                                    # This will result in a more readable report
                                    # tax and less cumbersome to analyse.
                                    if not line.account_id.user_type_id.block_entries:
                                        key = self._get_tax_cash_basis_base_key(
                                            tax, move, line)
                                        cash_basis_amount_dict[key] += rounded_amt
                                        cash_basis_amount_currency_dict[key] += line.currency_id.round(
                                            line.amount_currency * amount / line.balance) if line.currency_id and self.amount_currency else 0.0

                    if move_untax:
                        move_untax_id = move.id
                if cash_basis_amount_dict:
                    if not newly_created_move:
                        newly_created_move = self._create_tax_basis_move()
                    self._create_tax_cash_basis_base_line(
                        cash_basis_amount_dict,
                        cash_basis_amount_currency_dict, newly_created_move)
            self.recompute()
            if newly_created_move:
                # post move
                newly_created_move.write({'move_untaxed_id': move_untax_id})
                newly_created_move.post()
