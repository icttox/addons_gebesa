# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def cancel_invoice_refund(self):
        for invoice in self:
            if invoice.type not in ('out_refund', 'in_refund'):
                raise UserError(_(u"This invoice is not a credit note"))
            if invoice.date_invoice and not self.env.user.has_group(
                    'res_users_invoice_premonth.group_invoice_premonth'):
                date_inv = invoice.date_invoice.split('-', 3)
                today = str(fields.Date.today()).split('-', 3)
                if date_inv[1] != today[1] or date_inv[0] != today[0]:
                    raise UserError(
                        _("Can only cancel a movement of the same me in \
                           which it is realized.\nCheck with your \
                           system administrator."))
            for line in invoice.move_id.line_ids:
                if line.reconciled:
                    line.remove_move_reconcile()
            move = invoice.move_id
            invoice.write({'move_id': False})
            move.button_cancel()
            move.unlink()
        self.write({'state': 'cancel'})
