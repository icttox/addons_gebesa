# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.constrains('name', 'company_id', 'state')
    def _check_unique_name_company(self):
        for move in self:
            if move.state != 'draft':
                move_ids = self.search([
                    ('name', '=', move.name),
                    ('company_id', '=', move.company_id.id),
                    ('id', '!=', move.id)])
                if move_ids:
                    raise ValidationError(
                        _("You cannot have two moves with the same name!"))

    def delete_zeros(self):
        move_post = []
        for move in self:
            if move.amount == 0:
                move.unlink()
            else:
                for line in move.line_ids:
                    if line.debit == 0 and line.credit == 0:
                        line.unlink()
                move_post.append(move.id)
        return self.browse(move_post)

    def assigned_analytics(self, analytic_id=False):
        move_line_obj = self.env['account.move.line']
        self._cr.execute('UPDATE account_move '
                         'SET state=%s '
                         'WHERE id IN %s', ('draft', tuple([self._id]),))

        for move in self:
            resul = []
            for line in move.line_ids:
                analytic = line.analytic_account_id or False
                if not analytic:
                    resul.append(line.id)
            move_line_obj.write(resul, {'analytic_account_id': analytic_id})
            self.post()

    @api.multi
    def post(self, invoice=False):
        if not invoice:
            move_post = self.delete_zeros()
        else:
            move_post = self
        if not move_post:
            return
        for move in move_post:
            for line in move.line_ids:
                if line.account_id.required_partner and not line.partner_id:
                    raise ValidationError(_("Esta cuenta requiere partner"))
            if move.journal_id.foreign_currency:
                currency = move.line_ids[0].currency_id.id
                if any(currency != line.currency_id.id for line in move.line_ids):
                    raise ValidationError(_("The lines of the accounting policy \
                        have different currencies"))
        return super(AccountMove, move_post).post()

    @api.multi
    def reverse_moves(self, date=None, journal_id=None):
        for move in self:
            if not date:
                date = move.date
        return super().reverse_moves(
            date=date, journal_id=journal_id)

    @api.multi
    def lines_compute_amount_currency(self):
        for move in self:
            move.with_context({
                'check_move_validity': False
            }).line_ids._onchange_amount_currency()
