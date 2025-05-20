# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class AccountPayment(models.Model):
    _inherit = "account.payment"

    name = fields.Char(
        readonly=False,
        copy=False,
        default="Draft Payment"
    )

    @api.multi
    def post(self):
        if self.company_id.id == 9:
            for rec in self:
                if not rec.name:
                    super(AccountPayment, rec).post()
                else:
                    if rec.state != 'draft':
                        raise UserError(_("Only a draft payment can be posted. \
                                        Trying to post a payment in state %s.") %
                                        rec.state)

                    if any(inv.state != 'open' for inv in rec.invoice_ids):
                        raise ValidationError(
                            _("The payment cannot be processed because the \
                              invoice is not open!"))
                    # Create the journal entry
                    amount = rec.amount * \
                        (rec.payment_type in ('outbound', 'transfer') and 1 or -1)
                    move = rec._create_payment_entry(amount)

                    # In case of a transfer, the first journal entry created
                    # debited the source liquidity account and credited
                    # the transfer account. Now we debit the transfer account and
                    # credit the destination liquidity account.
                    if rec.payment_type == 'transfer':
                        transfer_credit_aml = move.line_ids.filtered(
                            lambda r:
                            r.account_id == rec.company_id.transfer_account_id)
                        transfer_debit_aml = rec._create_transfer_entry(amount)
                        (transfer_credit_aml + transfer_debit_aml).reconcile()

                    rec.state = 'posted'
        super().post()

    def _get_move_vals(self, journal=None):
        if self.company_id.id == 9:
            if not self.name:
                return super()._get_move_vals(journal)
            journal = journal or self.journal_id
            return {
                'name': self.name,
                'date': self.payment_date,
                'ref': self.communication or '',
                'company_id': self.company_id.id,
                'journal_id': journal.id,
            }
        return super()._get_move_vals(journal)
