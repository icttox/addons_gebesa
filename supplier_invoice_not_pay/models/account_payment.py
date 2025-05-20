# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api, _
from odoo.exceptions import UserError


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.multi
    def post(self):
        for rec in self:
            if any(inv.not_pay is True for inv in rec.invoice_ids):
                raise UserError(_("The payment cannot be processed because an Invoice(s) has the option of Not Pay! Check with the Purchasing Team this Information."))

        return super().post()
