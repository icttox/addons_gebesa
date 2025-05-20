# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    move_name = fields.Char(
        string='Journal Entry',
        readonly=False,
        default=False,
        copy=False,
        help="Technical field holding the number given to the invoice, \
        automatically set when the invoice is validated then stored \
        to set the same number again if the invoice is cancelled, \
        set to draft and re-validated.")

    @api.multi
    def do_cfdi_workflow(self):
        for line in self.invoice_line_ids:
            if line.product_id.bal_ini_prod:
                return []
        return super().do_cfdi_workflow()

    @api.multi
    def l10n_mx_edi_is_required(self):
        for line in self.invoice_line_ids:
            if line.product_id.bal_ini_prod:
                return False
        return super().l10n_mx_edi_is_required()


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.model
    def create(self, vals):
        line = super().create(vals)
        line.invoice_id.compute_taxes()
        return line
