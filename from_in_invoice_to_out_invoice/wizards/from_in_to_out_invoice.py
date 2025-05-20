# Copyright 2022, Cesar Barron
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountInvoiceInToOut(models.TransientModel):
    """Invoice from in to out"""

    _name = "account.invoice.in.to.out"
    _description = "Account Invoice from in to out"

    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        required=True,
        help="You can find a contact by its Name, TIN, Email or Internal Reference.")

    journal_id = fields.Many2one(
        'account.journal',
        string='Use Specific Journal',
        help='If empty, uses the journal of the journal entry to be reversed.')

    @api.multi
    def copy_in_to_out_invoice(self):
        invoice_ids = self._context.get('active_ids', False)
        res = self.env['account.invoice'].browse(
            invoice_ids).copy({
                'partner_id': self.partner_id.id,
                'type': 'out_invoice',
                'partner_bank_id': False,
                'journal_id': self.journal_id.id or False})
        if res:
            return {
                'name': _('Created Invoice'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'account.invoice',
                'domain': [('id', 'in', res.ids)],
            }
        return {'type': 'ir.actions.act_window_close'}
