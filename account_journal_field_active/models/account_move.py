# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, _, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.multi
    def post(self, invoice=False):
        for move in self:
            journal = move.journal_id
            if journal.active is False:
                raise UserError(_(u"The Journal %s cannot be used." % journal.name))

        if self.env.user.has_group('account_journal_field_active.group_accounting_restricted'):
            raise UserError(_("You do not have the permissions to validate this entry."))

        return super().post(invoice)
