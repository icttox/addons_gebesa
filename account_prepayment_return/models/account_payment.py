# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, _, fields, models
from odoo.exceptions import UserError


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    prepayment_type = fields.Selection(
        selection_add=[('advance_refund', 'Advance Refund')],
        default='normal',
    )

    advance_refund_id = fields.Many2one(
        'account.payment',
        string='Advance to Return',
    )

    @api.one
    @api.depends('invoice_ids', 'payment_type', 'partner_type', 'partner_id',
                 'prepayment_type')
    def _compute_destination_account_id(self):
        # if not self.partner_id.property_account_supplier_advance_id:
        #    raise UserError(_('You need to add the provider prepayment account.'))
        super()._compute_destination_account_id()
        if self.prepayment_type == 'advance_refund':
            if self.partner_id:
                if self.partner_type == 'customer':
                    self.destination_account_id = self.partner_id.\
                        property_account_customer_advance_id.id
                else:
                    self.destination_account_id = self.partner_id.\
                        property_account_supplier_advance_id.id

    @api.multi
    def post(self):
        move_line_obj = self.env['account.move.line']
        if self.prepayment_type == 'advance':
            if self.payment_type == 'outbound':
                if not self.partner_id.property_account_supplier_advance_id:
                    raise UserError(_('You need to add an advance account.'))
            if self.payment_type == 'inbound':
                if not self.partner_id.property_account_customer_advance_id:
                    raise UserError(_('You need to add an advance account.'))
        res = super().post()
        for rec in self:
            if rec.advance_refund_id and \
               rec.prepayment_type == 'advance_refund':
                if rec.advance_refund_id.payment_date > rec.payment_date:
                    raise UserError(_('Error!'
                                      '\nThe date of the advance may'
                                      'not exceed the date of the return.'))
                adv_amount = rec.advance_refund_id.pending_amount
                ret_amount = rec.amount
                if ret_amount > adv_amount:
                    raise UserError(_('Error!'
                                      '\nThe amount of the refund must be less'
                                      'or equal to the amount of the advance'))
                total = adv_amount - ret_amount
                rec.advance_refund_id.pending_amount = total
                lines_refund = move_line_obj.search(
                    [('payment_id', '=', rec.id),
                     ('account_id', '=', rec.destination_account_id.id)])
                lines_advance = move_line_obj.search(
                    [('payment_id', '=', rec.advance_refund_id.id),
                     ('account_id', '=', rec.destination_account_id.id)])
                (lines_refund + lines_advance).reconcile(
                    False, rec.journal_id.id)

                rec.state = 'reconciled'
                if total == 0.0:
                    rec.advance_refund_id.state = 'reconciled'
                    rec.advance_refund_id.pending_amount = 0.0

            return res

    @api.multi
    def cancel(self):
        res = super().cancel()
        for rec in self:
            if rec.advance_refund_id and \
               rec.prepayment_type == 'advance_refund':
                total_adv = rec.advance_refund_id.pending_amount
                total_dev = rec.amount
                total = total_adv + total_dev
                rec.advance_refund_id.pending_amount = total

            return res
