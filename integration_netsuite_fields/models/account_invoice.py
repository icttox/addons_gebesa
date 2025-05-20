# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountInvoice(models.Model):
    _name = 'account.invoice'
    _inherit = 'account.invoice'

    msj = fields.Text(
        string='Last Message',
        readonly=True,
        track_visibility='onchange',
        help='Message generated to upload XML to sign',
    )

    netsuite_ok = fields.Boolean(
        string='Netsuite Updated',
        help='It indicates whether update the order status in NetSuite',
        readonly=True,
        store=True,
    )
