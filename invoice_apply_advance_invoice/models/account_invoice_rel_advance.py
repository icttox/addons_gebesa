# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountInvoiceRelAdvance(models.Model):
    _name = 'account.invoice.rel.advance'
    _description = 'descripcion pendiente'

    invoice_id = fields.Many2one(
        'account.invoice',
        string='Invoice',
        ondelete='cascade',
    )
    advance_id = fields.Many2one(
        'account.invoice',
        string='Advance',
        ondelete='cascade',
    )
    amount_advance = fields.Float(
        string='Amount Advance',
    )

    @api.constrains('amount_advance')
    def _check_qty_segmented(self):
        for line in self:
            if line.amount_advance < 0:
                raise UserError(_("The amount must be greater than zero \n"
                                  "verify the advance amount please"))

    @api.onchange('advance_id')
    def _onchange_advance_id(self):
        advance = self.advance_id
        if advance:
            if advance.amount_residual_advance >= self.invoice_id.amount_total:
                self.amount_advance = self.invoice_id.amount_total
            else:
                self.amount_advance = advance.amount_residual_advance
        return
