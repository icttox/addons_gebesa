# © 2021, Leslie Marquez.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    amount_currency = fields.Monetary("Amount in currency", compute="_compute_amount_currency", currency_field='currency_id', readonly=True, store=True)

    @api.multi
    @api.depends("currency_id", "rate_mex", "amount")
    def _compute_amount_currency(self):
        for rec in self:
            rec.amount_currency = (rec.rate_mex * rec.amount)
