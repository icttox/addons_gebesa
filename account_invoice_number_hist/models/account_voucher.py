# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    number = fields.Char(
        readonly=False,
        copy=False
    )
