# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountInvoiceRefund(models.TransientModel):
    _inherit = 'account.invoice.refund'

    replacement = fields.Boolean(
        string='Replacement',
    )

    responsible_id = fields.Many2one(
        'res.users',
        string='Responsible',
    )
