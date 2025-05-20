# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    term_defer = fields.Integer(
        string='Term to defer',
    )
    months_deferred = fields.Integer(
        string='Months to be deferred',
    )
    account_defer_id = fields.Many2one(
        'account.account',
        string='Account to defer',
    )
    journal_defer_id = fields.Many2one(
        'account.journal',
        string='Journal to defer',
    )

    @api.onchange('term_defer')
    def _onchange_months_deferred(self):
        self.months_deferred = self.term_defer

    @api.multi
    def invoice_validate(self):
        for inv in self:
            if inv.term_defer != inv.months_deferred:
                raise UserError(_(
                    'The term to be deferred and the months to be deferred are\
                     different, please review '))
        return super().invoice_validate()

    @api.model
    def deferred_assets(self):
        am_obj = self.env['account.move']
        aml_obj = self.env['account.move.line']
        invoice = self.search([
            ('state', 'in', ['open', 'paid']),
            ('months_deferred', '>', 0)
        ], order='date_invoice')
        for inv in invoice:
            am_vals = {
                'journal_id': inv.journal_defer_id.id,
                'date': fields.Datetime.now(),
                'ref': _('Deferred assets invoice %s') % inv.number,
                'company_id': inv.company_id.id,
            }
            am_id = am_obj.create(am_vals)
            ctx = self._context.copy()
            ctx.update({'check_move_validity': False})
            total_amount = 0.0
            for line in inv.move_id.line_ids:
                if not (line.product_id and line.invoice_id):
                    continue
                amount = round(line.debit / inv.term_defer, 4)
                total_amount += amount
                vals = {
                    'move_id': am_id.id,
                    'partner_id': inv.partner_id.id,
                    'journal_id': inv.journal_defer_id.id,
                    'date': fields.Datetime.now().date(),
                    'product_id': line.product_id.id,
                    'credit': amount,
                    'name': _('Deferred assets %s') % line.name,
                    'account_id': line.account_id.id,
                    'analytic_account_id': inv.account_analytic_id.id,
                    'debit': 0.0,
                    'operating_unit_id': inv.operating_unit_id.id,
                }
                aml_obj.with_context(ctx).create(vals)
            vals = {
                'move_id': am_id.id,
                'partner_id': inv.partner_id.id,
                'journal_id': inv.journal_defer_id.id,
                'date': fields.Datetime.now().date(),
                # 'product_id': line.product_id.id,
                'credit': 0.0,
                'name': _('Deferred assets'),
                'account_id': inv.account_defer_id.id,
                'analytic_account_id': inv.account_analytic_id.id,
                'debit': total_amount,
                'operating_unit_id': inv.operating_unit_id.id,
            }
            aml_obj.with_context(ctx).create(vals)
            am_id.post()
            inv.months_deferred -= 1
        return True
