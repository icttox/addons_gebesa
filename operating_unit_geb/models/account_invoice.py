# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'


    @api.onchange('operating_unit_id')
    def _onchange_operating_unit(self):
        if self.operating_unit_id and (
                not self.journal_id or
                self.journal_id.operating_unit_id != self.operating_unit_id):
            journal = self._default_journal()
            jf = journal.filtered(
                lambda aj: aj.operating_unit_id == self.operating_unit_id)
            if not jf:
                self.journal_id = journal[0]
            else:
                self.journal_id = jf[0]
