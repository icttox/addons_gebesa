# -*- coding: utf-8 -*-
# Copyright 2020, Cesar Barron
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.multi
    def remove_move_voucher_reconcile(self):
        """ Undo a reconciliation """
        if not self:
            return True
        rec_move_ids = self.env['account.partial.reconcile']
        for account_move_line in self:
            for voucher in account_move_line.payment_id.voucher_ids:
                if voucher.id == self.env.context.get(
                        'default_voucher_id') and account_move_line in voucher.payment_move_line_ids:
                    account_move_line.payment_id.write(
                        {'voucher_ids': [(3, voucher.id, None)]})
            rec_move_ids += account_move_line.matched_debit_ids
            rec_move_ids += account_move_line.matched_credit_ids
        return rec_move_ids.unlink()


class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    payment_move_line_ids = fields.Many2many(
        'account.move.line',
        string='Payments',
        compute='_compute_payments',
        store=True
    )

    @api.one
    @api.depends('move_id.line_ids.amount_residual')
    def _compute_payments(self):
        payment_lines = []
        for line in self.move_id.line_ids.filtered(
                lambda l: l.account_id.id == self.account_id.id):
            payment_lines.extend(
                filter(None, [rp.credit_move_id.id for rp in line.matched_credit_ids]))
            payment_lines.extend(
                filter(None, [rp.debit_move_id.id for rp in line.matched_debit_ids]))
        self.payment_move_line_ids = self.env['account.move.line'].browse(
            list(set(payment_lines)))
