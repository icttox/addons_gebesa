# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountAccount(models.Model):
    _inherit = 'account.account'

    edores_type_id = fields.Many2one(
        'account.account.edores.type',
        string='Income Statement',
    )
