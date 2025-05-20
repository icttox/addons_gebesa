# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def action_move_create(self):
        if self.date_invoice and not self.env.user.has_group(
                'res_users_invoice_premonth.group_invoice_premonth'):
            date_inv = str(self.date_invoice).split('-', 3)
            today = str(fields.Date.today()).split('-', 3)
            if date_inv[1] != today[1] or date_inv[0] != today[0]:
                raise ValidationError(_(u"You do not have privileges to \
                                      register invoices months different from \
                                      the current.\n Instead you should ask \
                                      accounting that records the invoice"))
        super().action_move_create()
