# -*- coding: utf-8 -*-
# © <2021> <Samuel Barron Bautista>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.model
    def _get_payments_vals(self):
        res = super()._get_payments_vals()

        for pay in res:
            aml = self.env['account.move.line'].search(
                [('id', '=', pay['payment_id'])])
            if aml.invoice_id and aml.payment_id:
                pay['invoice_id'] = False
        return res
