# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.tools import float_is_zero


class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    payment_ids = fields.Many2many(
        'account.payment',
        string='Payment',
    )
    amount_pending = fields.Float(
        string='Amount Pending',
        compute="compute_amount_pending"
    )

    @api.depends(
        'state', 'currency_id',
        'move_id.line_ids.amount_residual',
        'move_id.line_ids.currency_id')
    def compute_amount_pending(self):
        for voucher in self:
            residual = 0.0
            # sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
            for line in voucher.move_id.line_ids:
                if line.account_id.internal_type in ('receivable', 'payable'):
                    if line.currency_id == voucher.currency_id:
                        residual += line.amount_residual_currency \
                            if line.currency_id else line.amount_residual
                    else:
                        from_currency = (line.currency_id and
                                         line.currency_id.with_context(
                                             date=line.date)) or \
                            line.company_id.currency_id.with_context(
                                date=line.date)
                        # residual += from_currency.compute(line.amount_residual,
                        #                                   voucher.currency_id)
                        residual += from_currency._convert(line.amount_residual, voucher.currency_id, voucher.company_id, line.date)
            voucher.amount_pending = abs(residual)
            digits_rounding_precision = voucher.currency_id.rounding
            if float_is_zero(voucher.amount_pending,
                             precision_rounding=digits_rounding_precision):
                voucher.paid = True
            else:
                voucher.paid = False

    def register_payment(self, aml_payment=False):
        if not aml_payment:
            return
        line_to_reconcile = self.env['account.move.line']
        for vou in self:
            line_to_reconcile += vou.move_id.line_ids.filtered(
                lambda r: not r.reconciled and r.account_id.internal_type in (
                    'payable', 'receivable'))
        return (line_to_reconcile + aml_payment).reconcile()
