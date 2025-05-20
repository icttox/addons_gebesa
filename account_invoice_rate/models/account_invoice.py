# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountInvoice(models.Model):
    _name = 'account.invoice'
    _inherit = 'account.invoice'

    rate = fields.Float(
        string='Type of change',
        help='Rate used in the date of invoice',
        compute='_compute_rate',
        store=True,
    )

    @api.multi
    @api.depends('currency_id', 'date_invoice')
    def _compute_rate(self):
        for inv in self:
            currency_id = inv.currency_id
            currency_from_id = inv.company_id.currency_id
            rate = currency_from_id._convert(
                1, currency_id, inv.company_id,
                inv.date_invoice or fields.Date.today())
            inv.rate = rate
