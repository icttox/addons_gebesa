# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from ast import literal_eval
from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    prepayment_ok = fields.Boolean(
        string='Advance Invoice',
        copy=False,
    )

    advance_applied = fields.Boolean(
        string='Advance Applied',
        help='The advance has already been applied',
        copy=False,
    )

    amount_residual_advance = fields.Float(
        string='Amount Residual Advance',
        copy=False,
    )

    note_applied = fields.Boolean(
        string='Nota de Credito aplicada',
        copy=False,
    )

    @api.multi
    def action_move_create(self):
        if self.type == 'out_invoice':
            for line in self.invoice_line_ids:
                product = line.product_id.id
                deposit = literal_eval(self.env[
                    'ir.config_parameter'].sudo().get_param(
                        'sale.default_deposit_product_id', 'False'))
                if product == int(deposit) and line.price_subtotal > 0:
                    self.prepayment_ok = True
                    self.amount_residual_advance = self.amount_total

        return super().action_move_create()
