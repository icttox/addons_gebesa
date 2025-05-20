# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    dev_tipo = fields.Selection(
        [('normal', 'Normal'),
         ('rebilling', 'Rebilling'),
         ('cancellation', 'Cancellation')],
        string="Type",
        help="defines the type"
    )
