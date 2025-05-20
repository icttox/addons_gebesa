# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountInvoiceRefund(models.TransientModel):
    _inherit = "account.invoice.refund"

    not_sing_invoice_refund = fields.Boolean(
        string='No timbrar NC',
    )

    @api.onchange('filter_refund')
    def _onchange_filter_refund(self):
        self.not_sing_invoice_refund = False

    @api.multi
    def compute_refund(self, mode='refund'):
        ctx = self._context.copy()
        ctx.update({
            'default_not_sing_invoice_refund': self.not_sing_invoice_refund})
        return super(AccountInvoiceRefund, self.with_context(
            ctx)).compute_refund(mode=mode)
