# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    date_invoice = fields.Date(string='Invoice Date', index=True, states={},
    	help="Keep empty to use the current date", copy=False)
