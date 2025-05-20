# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from ast import literal_eval
import datetime
from odoo import api, models
from odoo.exceptions import UserError


class AccountInvoiceRefund(models.TransientModel):
    _inherit = 'account.invoice.refund'

    @api.multi
    def compute_refund(self, mode='refund'):
        context = dict(self._context or {})
        context.update({'mode': mode})
        invoice = self.env['account.invoice'].browse(
            self._context.get('active_id', False))
        invoice.mode = mode
        deposit = literal_eval(self.env[
            'ir.config_parameter'].sudo().get_param(
                'sale.default_deposit_product_id')) or False
        total_advance = 0.0
        if self.filter_refund == 'refund':
            if self.product_id.id == deposit:
                date_val = datetime.datetime.strptime('2019-10-07', '%Y-%m-%d').date()
                account_deposit = invoice.partner_id.mapped('property_account_customer_advance_id')
                if not account_deposit:
                    raise UserError('Este cliente no tiene una cuenta de anticipo asignada')
                for advance in invoice.advance_ids:
                    line_reconcile = advance.advance_id.mapped('move_id').mapped(
                        'line_ids').filtered(
                        lambda l: l.account_id == account_deposit)
                    residual_advance = sum(line_reconcile.mapped('amount_residual'))
                    if advance.advance_id.invoice_line_ids[0].invoice_line_tax_ids:
                        amount_advance = advance.amount_advance / 1.16
                    else:
                        amount_advance = advance.amount_advance
                    if (abs(round(residual_advance, 6)) - round(amount_advance, 6)) < -0.05:
                        raise UserError(
                            'Saldo insuficiente en el anticipo %s (%s|%s)' % (
                                advance.advance_id.number,
                                round(residual_advance, 6),
                                round(amount_advance, 6)))
                    total_advance += advance.amount_advance
                if abs(total_advance - self.amount) > 0.50 and invoice.date_invoice > date_val:
                    raise UserError('Debe aplicar el total de los anticipos')

                invoice.note_applied = True

        res = super().compute_refund(invoice.mode)
        return res
