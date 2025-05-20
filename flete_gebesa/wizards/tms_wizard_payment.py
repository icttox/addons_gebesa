# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, _
from odoo.exceptions import ValidationError, UserError


class TmsWizardPayment(models.TransientModel):
    _inherit = 'tms.wizard.payment'

    @api.multi
    def _create_payment(self, counterpart_move_line, record):
        super()._create_payment(counterpart_move_line,
                                                      record)
        obj_payment = self.env['account.payment']
        operating_unit_payment = self.env['operating.unit']
        payment = obj_payment.browse([counterpart_move_line['payment_id']])
        operating = operating_unit_payment.browse(
            [counterpart_move_line['operating_unit_id']])
        payment.write({
            'account_analytic_id': operating.analytic_account_id.id
        })

    @api.multi
    def make_payment(self):
        for rec in self:
            active_ids = self.env[self._context.get('active_model')].browse(
                self._context.get('active_ids'))
            active_model = self._context['active_model']
            bank_account_id = rec.journal_id.default_debit_account_id.id

            if not bank_account_id:
                raise UserError("La cuenta bancaria no tiene asignada una cuenta deudora por defecto")

            employee_id = set([x.employee_id.id for x in active_ids])
            if len(employee_id) > 1:
                raise ValidationError(
                    _('You cannot pay documents for different driver'))

            acc_number = ''
            employee_id = active_ids[0].employee_id
            if rec.journal_id.bank_acc_number:
                if not employee_id.bank_account_id or not employee_id.bank_account_id.acc_number:
                    raise ValidationError(
                        _('The driver %s does not have a bank account_assigned') % employee_id.name)
                acc_number = employee_id.bank_account_id.acc_number

            currency = rec.journal_id.currency_id or self.env.user.currency_id
            currency_id = set([x.currency_id.id for x in active_ids])
            if len(currency_id) > 1:
                raise ValidationError(
                    _('You cannot pay documents for different currency'))
            if currency.id != list(currency_id)[0]:
                raise ValidationError(
                    _('You cannot pay documents in different currency of the '
                      'bank (%s)' % rec.journal_id.currency_id.name))
            move_lines = []
            amount_bank = 0.0
            amount_currency = 0.0
            name = 'Payment of'
            bank_line = {}
            for obj in active_ids:
                name = name + ' / ' + obj.name
                if obj.state not in ['confirmed', 'closed'] or obj.paid:
                    raise ValidationError(
                        _('The document %s must be confirmed and '
                          'unpaid.') % obj.name)
                counterpart_move_line = {
                    'name': obj.name,
                    'account_id': (
                        obj.employee_id.address_home_id.
                        property_account_payable_id.id),
                    'credit': 0.0,
                    'journal_id': rec.journal_id.id,
                    'partner_id': obj.employee_id.address_home_id.id,
                    'operating_unit_id': obj.operating_unit_id.id,
                }
                model_amount = {
                    'tms.advance': obj.amount
                    if hasattr(obj, 'amount') and
                    active_model == 'tms.advance' else 0.0,
                    'tms.expense': obj.amount_balance
                    if hasattr(obj, 'amount_balance') and
                    active_model == 'tms.expense' else 0.0,
                    'tms.expense.loan': obj.amount
                    if hasattr(obj, 'amount') and
                    active_model == 'tms.expense.loan'else 0.0}
                # Creating counterpart move lines method explained above
                counterpart_move_line, amount_bank = self.create_counterpart(
                    model_amount, currency, obj,
                    amount_currency, amount_bank, counterpart_move_line)
                # self._create_payment(counterpart_move_line, rec)
                move_lines.append((0, 0, counterpart_move_line))
                if amount_currency > 0.0:
                    bank_line['amount_currency'] = amount_currency
                    bank_line['currency_id'] = currency.id
                    # TODO Separate the bank line for each Operating Unit
            operating_unit_id = self.env['operating.unit'].search(
                [], limit=1)
            payment_dict = {
                'journal_id': counterpart_move_line['journal_id'],
                'partner_id': counterpart_move_line['partner_id'],
                'operating_unit_id': counterpart_move_line['operating_unit_id'],
                'debit': amount_bank,
                'name': name
            }
            self._create_payment(payment_dict, rec)
            bank_line = {
                'name': name,
                'account_id': bank_account_id,
                'debit': 0.0,
                'credit': amount_bank,
                'journal_id': rec.journal_id.id,
                'operating_unit_id': operating_unit_id.id,
                'acc_number': acc_number
            }
            move_lines.append((0, 0, bank_line))
            for line in move_lines:
                line[2]['payment_id'] = payment_dict['payment_id']
                line[2]['analytic_account_id'] = (
                    operating_unit_id.analytic_account_id.id)
            move = {
                'date': rec.date,
                'journal_id': rec.journal_id.id,
                'ref': name,
                'line_ids': [line for line in move_lines],
                'narration': rec.notes,
            }
            # Creating moves and reconciles method explained above
            rec.create_moves_and_reconciles(move, active_ids)

    @api.multi
    def create_moves_and_reconciles(self, move, active_ids):
        super().create_moves_and_reconciles(
            move, active_ids)
        for obj in active_ids:
            obj.payment_move_id.line_ids[0].payment_id.name = obj.payment_move_id.name
