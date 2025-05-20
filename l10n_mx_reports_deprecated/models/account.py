# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from __future__ import division

from odoo import api, models


class AccountPartialReconcileCashBasis(models.Model):
    _inherit = 'account.partial.reconcile'

    @api.model
    def create(self, vals):
        """When is created the record, is generated a new journal entry with
        taxes data, but the partner is not assigned to the moves, due to the
        fact that the partner is required in the DIOT report we force to set a
        partner when necessary for such report."""
        # TODO - This must be in the Odoo module (account_tax_cash_basis)
        res = super(AccountPartialReconcileCashBasis, self).create(vals)
        move_tax = self.env['account.move'].search(
            [('tax_cash_basis_rec_id', '=', res.id)])
        invoice_obj = self.env['account.invoice']
        invoice = invoice_obj.search([
            '|', ('move_id', '=', res.debit_move_id.move_id.id),
            ('move_id', '=', res.credit_move_id.move_id.id)])
        number = ', '.join(invoice.mapped('number'))
        move_tax.write({
            'partner_id': res.credit_move_id.partner_id.id,
            'ref': number or move_tax.ref,
        })
        move_tax.line_ids.write({
            'partner_id': res.credit_move_id.partner_id.id,
        })
        if invoice:
            move_tax.line_ids.write({'name': number})
        return res
