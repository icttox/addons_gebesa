# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    def _get_dst_liquidity_aml_dict_vals(self):
        dst_liquidity_aml_dict = {
            'name': _('Transfer from %s') % self.journal_id.name,
            'account_id':
                self.destination_journal_id.default_credit_account_id.id,
            'currency_id': self.destination_journal_id.currency_id.id,
            'payment_id': self.id,
            'journal_id': self.destination_journal_id.id,
        }

        if self.currency_id != self.company_id.currency_id:
            dst_liquidity_aml_dict.update({
                'currency_id': self.currency_id.id,
                # 'amount_currency': -self.amount,
            })

        dst_liquidity_aml_dict.update({
            'operating_unit_id':
                self.destination_journal_id.operating_unit_id.id or False})
        return dst_liquidity_aml_dict

    @api.multi
    def cancel(self):
        for rec in self:
            if rec.payment_type == 'transfer':
                for line in rec.move_line_ids:
                    if line.reconciled:
                        line.remove_move_reconcile()
        return super().cancel()
