# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.multi
    def post(self, invoice=False):
        for move in self:
            for line in move.line_ids:
                if line.account_id.user_type_id.block_entries:
                    raise UserError(_(
                        'This account type(%s) doesn´t allow account entries'
                    ) % (line.account_id.user_type_id.name))
        return super().post(invoice)
