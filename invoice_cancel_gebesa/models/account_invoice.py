# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    invoice_refacture_id = fields.Many2one(
        'account.invoice',
        string='Rebilling Number',
    )

    reason_cancellation = fields.Text(
        string='Reason for Cancellation',
    )
