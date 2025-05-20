# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, fields, models


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    voucher_ids = fields.Many2many(
        'account.voucher',
        string='Voucher',
    )
    voucher_pay_id = fields.Many2one(
        'account.voucher.payment',
        string='Voucher Payment',
    )

    def _get_voucher_move_line_vals(self, move_id=False):
        aml_obj = self.env[
            'account.move.line'].with_context(check_move_validity=False)
        move_lines = []
        name = ''
        customer_pay = True
        if self.partner_type == 'customer':
            if self.payment_type == 'inbound':
                name += _(u"Customer Payment")
            elif self.payment_type == 'outbound':
                name += _(u"Customer Refund")
                customer_pay = False
        elif self.partner_type == 'supplier':
            if self.payment_type == 'inbound':
                name += _(u"Vendor Refund")
            elif self.payment_type == 'outbound':
                name += _(u"Vendor Payment")
                customer_pay = False

        for rec in self:
            vou_pay = self.env[
                'account.voucher.payment'].browse(
                    [rec.voucher_pay_id.id])
            for line in vou_pay.line_ids:
                name_line = name + ":" + line.voucher_id.number
                credit, debit, amount_currency, currency_id = \
                    aml_obj.with_context(
                        date=rec.payment_date)._compute_amount_fields(
                            line.amount,
                            rec.currency_id,
                            rec.company_id.currency_id)

                move_line = {
                    'partner_id': rec.payment_type in
                    ('inbound', 'outbound') and
                    self.env['res.partner']._find_accounting_partner(
                        rec.partner_id).id or False,
                    'voucher_id': line.voucher_id and
                    line.voucher_id.id or False,
                    'move_id': move_id,
                    'debit': debit if customer_pay else credit,
                    'credit': credit if customer_pay else debit,
                    'amount_currency': amount_currency or False,
                    'name': name_line,
                    'account_id': rec.destination_account_id.id,
                    'journal_id': rec.journal_id.id,
                    'currency_id': rec.currency_id !=
                    rec.company_id.currency_id and
                    currency_id or False,
                    'payment_id': rec.id,
                }
                if move_line['credit'] > 0:
                    amount_currency = move_line['amount_currency'] * -1
                    move_line['amount_currency'] = amount_currency
                move_lines.append(move_line)
        return move_lines

    def _create_payment_entry(self, amount):
        """ Create a journal entry corresponding to a payment, if the payment
            references invoice(s) they are reconciled.
            Return the journal entry.
        """
        if not self.voucher_pay_id and not self.voucher_pay_id.id:
            res = super()._create_payment_entry(amount)
            return res

        aml_obj = self.env[
            'account.move.line'].with_context(check_move_validity=False)
        debit, credit, amount_currency, currency_id = \
            aml_obj.with_context(
                date=self.payment_date)._compute_amount_fields(
                    amount, self.currency_id, self.company_id.currency_id)

        move = self.env['account.move'].create(self._get_move_vals())

        # Write line corresponding to invoice payment
        counterpart_aml_dict = self._get_voucher_move_line_vals(
            move.id)

        for aml_cont in counterpart_aml_dict:
            counterpart_aml = aml_obj.create(aml_cont)

            self.env['account.voucher'].browse(
                aml_cont['voucher_id']).register_payment(counterpart_aml)

        # Write counterpart lines
        liquidity_aml_dict = self._get_shared_move_line_vals(
            credit, debit, -amount_currency, move.id, False)
        liquidity_aml_dict.update(self._get_liquidity_move_line_vals(-amount))
        aml_obj.create(liquidity_aml_dict)

        move.post()
        return move
