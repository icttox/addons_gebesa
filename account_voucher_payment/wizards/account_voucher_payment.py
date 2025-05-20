# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, exceptions, fields, models
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError


class AccountVoucherPayment(models.Model):
    _name = 'account.voucher.payment'
    _description = 'descripcion pendiente'

    journal_id = fields.Many2one(
        'account.journal',
        string=_('Payment method'),
        domain=[('type', 'in', ('bank', 'cash'))],
        required=True,
    )
    payment_method_id = fields.Many2one(
        'account.payment.method',
        string='Payment Type',
        required=True,
    )
    amount = fields.Monetary(
        string=_('Payment amount'),
    )
    date = fields.Date(
        string=_('Payment date'),
        default=fields.Date.context_today,
        copy=False,
    )
    communication = fields.Char(
        string=_('Memo'),
    )
    analytic_id = fields.Many2one(
        'account.analytic.account',
        string=_('Analytic account'),
    )
    company_id = fields.Many2one(
        'res.company',
        related='journal_id.company_id',
        string='Company',
        readonly=True
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        required=True,
        default=lambda self: self.env.user.company_id.currency_id
    )
    payment_type = fields.Selection(
        [('outbound', 'Send Money'), ('inbound', 'Receive Money')],
        string='Payment Type',
        required=True
    )
    partner_type = fields.Selection(
        [('customer', 'Customer'), ('supplier', 'Vendor')]
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner'
    )
    line_ids = fields.One2many(
        'account.voucher.payment.line',
        'register_payment_id',
        string=_("Voucher")
    )

    @api.constrains('amount')
    def _check_total_mustbe_sum_of_lines(self):
        for rec in self:
            if rec.line_ids:
                total_amount_lines = 0.00
                for line in rec.line_ids:
                    total_amount_lines += line.amount
                difference = rec.amount - total_amount_lines
                if abs(difference) > 0.05:
                    raise exceptions.ValidationError(_(u"The sum of the amount to \
                                                     pay per voucher '%d'\
                                                     must be equal than \
                                                     the payment amount '%s'")
                                                     % (total_amount_lines,
                                                        rec.amount))

    @api.onchange('journal_id')
    def _onchange_journal(self):
        if self.journal_id:
            self.currency_id = self.journal_id.currency_id or \
                self.company_id.currency_id
            # Set default payment method (we consider the first to be the
            # default one)
            payment_methods = self.payment_type == 'inbound' and \
                self.journal_id.inbound_payment_method_ids or \
                self.journal_id.outbound_payment_method_ids
            self.payment_method_id = payment_methods and payment_methods[
                0] or False
            # Set payment method domain (restrict to methods enabled for the
            # journal and to selected payment type)
            payment_type = self.payment_type in (
                'outbound', 'transfer') and 'outbound' or 'inbound'
            return {'domain': {'payment_method_id': [(
                'payment_type', '=', payment_type), (
                'id', 'in', payment_methods.ids)]}}
        return {}

    @api.model
    def default_get(self, fields_list):
        rec = super().default_get(fields_list)
        context = dict(self._context or {})
        active_model = context.get('active_model')
        active_ids = context.get('active_ids')

        # Checks on context parameters
        if not active_model or not active_ids:
            raise UserError(_(u"Programmation error: \
                            wizard action executed without active_model \
                            or active_ids in context."))
        if active_model != 'account.voucher':
            raise UserError(_(u"Programmation error: the expected model \
                            for this action is 'account.voucher'. \
                            The provided one is '%d'.") % active_model)

        # Checks on received invoice records
        vouchers = self.env[active_model].browse(active_ids)
        lines = []
        aml_ids = False
        account_type = False

        if any(voucher.state != 'posted' for voucher in vouchers):
            raise UserError(
                _("You can only register payments for posted voucher"))
        if any(
                vou.partner_id.commercial_partner_id !=
                vouchers[0].partner_id.commercial_partner_id
                for vou in vouchers):
            raise UserError(
                _("In order to pay multiple vouchers at once, they must \
                  belong to the same commercial partner."))
        if any(vou.voucher_type != vouchers[0].voucher_type
               for vou in vouchers):
            raise UserError(
                _("You cannot mix customer vouchers and vendor bills in a \
                   single payment."))
        if any(vou.currency_id != vouchers[0].currency_id for vou in vouchers):
            raise UserError(_("In order to pay multiple vouchers at once, \
                they must use the same currency."))

        if any(voucher.voucher_type == 'sale' for voucher in vouchers):
            account_type = 'receivable'
        elif any(voucher.voucher_type == 'purchase' for voucher in vouchers):
            account_type = 'payable'

        total_amount = 0

        # Fill the defaults values of the selected invoices
        for vou in vouchers:
            if vou.paid:
                continue
            aml_ids = self.env[
                'account.move.line'].search([
                                            ('account_id.internal_type', '=',
                                             account_type),
                                            ('full_reconcile_id', '=', False),
                                            ('move_id', '=', vou.move_id.id)],
                                            limit=1,
                                            order='date_maturity')
            account_id = aml_ids[0].account_id.id
            analytic_id = aml_ids[0].analytic_account_id.id
            aprl = {
                'voucher_id': vou.id,
                'reconcile': True,
                'move_line_id': aml_ids[0].id,
                'date_original': vou.date,
                'date_due': vou.date_due,
                'partner_id': vou.partner_id.id,
                'company_id': vou.company_id.id,
                'currency_id': vou.currency_id.id,
                'name': vou.number,
                'reference': vou.reference,
                'account_id': account_id,
                'account_analytic_id': analytic_id,
                'amount_original': vou.amount,
                'amount_unreconciled': vou.amount_pending,
                'amount': vou.amount_pending
            }
            total_amount += aml_ids[
                0].amount_residual_currency or aml_ids[0].amount_residual
            lines.append([0, False, aprl])
        rec.update({
            'line_ids': lines,
        })
        rec.update({
            'amount': abs(total_amount),
            'currency_id': vouchers[0].currency_id.id,
            'payment_type': total_amount > 0 and 'inbound' or 'outbound',
            'partner_id': vouchers[0].partner_id.commercial_partner_id.id,
            'partner_type': vouchers[0].voucher_type == 'sale' and 'customer' or 'supplier',
        })
        return rec

    def _get_vouchers(self):
        return self.env['account.voucher'].browse(
            self._context.get('active_ids'))

    def get_payment_vals(self):
        """ Hook for extension """
        return {
            'journal_id': self.journal_id.id,
            'payment_method_id': self.payment_method_id.id,
            'payment_date': self.date,
            'communication': self.communication,
            'voucher_ids': [(4, vou.id, None) for vou in self._get_vouchers()],
            'payment_type': self.payment_type,
            'amount': self.amount,
            'currency_id': self.currency_id.id,
            'partner_id': self.partner_id.id,
            'partner_type': self.partner_type,
            'account_analytic_id': self.analytic_id.id,
            'voucher_pay_id': self.id
        }

    @api.multi
    def create_payment(self):
        payment = self.env['account.payment'].create(self.get_payment_vals())
        payment.post()
        return {'type': 'ir.actions.act_window_close'}


class AccountVoucherPaymentLine(models.Model):
    _name = 'account.voucher.payment.line'
    _description = 'descripcion pendiente'

    register_payment_id = fields.Many2one(
        'account.voucher.payment',
        string=_("Register payment"),
        required=True,
        ondelete='cascade'
    )
    voucher_id = fields.Many2one(
        'account.voucher',
        string=_('Voucher'),
    )
    reconcile = fields.Boolean(
        string=_("Full Reconcile")
    )
    move_line_id = fields.Many2one(
        'account.move.line',
        string=_("Journal Item"),
    )
    date_original = fields.Date(
        related='move_line_id.date',
        string=_("Date"),
        readonly=True,
    )
    date_due = fields.Date(
        related='move_line_id.date_maturity',
        string=_("Due Date"),
        readonly=True,
    )
    partner_id = fields.Many2one(
        related='register_payment_id.partner_id',
        string=_("Partner"),
        readonly=True,
        store=True
    )
    company_id = fields.Many2one(
        related='register_payment_id.company_id',
        string=_("Company"),
        store=True,
        readonly=True
    )
    currency_id = fields.Many2one(
        related='register_payment_id.currency_id',
        string=_("Currency"),
        readonly=True,
        store=True
    )
    name = fields.Char(
        string=_("Reference/Description"),
        readonly=True
    )
    reference = fields.Char(
        string=_("Vendor Reference"),
        readonly=True
    )
    account_id = fields.Many2one(
        'account.account',
        'Account',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        domain="[('deprecated', '=', False),\
            ('internal_type','=', (pay_now == 'pay_now' and 'liquidity' \
            or voucher_type == 'purchase' and 'payable' or 'receivable'))]")

    untax_amount = fields.Float(
        string=_("Untax Amount"),
        digits=dp.get_precision('Account')
    )
    amount = fields.Float(
        string=_("Amount"),
        digits=dp.get_precision('Account')
    )
    amount_original = fields.Float(
        string=_("Original Amount"),
        store=True,
        digits=dp.get_precision('Account')
    )
    amount_unreconciled = fields.Float(
        string=_("Open Balance"),
        store=True,
        digits=dp.get_precision('Account')
    )

    @api.onchange('amount')
    def _verify_full_reconcile(self):
        if self.amount == self.amount_unreconciled:
            self.reconcile = True
        else:
            self.reconcile = False

        if self.amount > self.amount_unreconciled:
            return {
                'warning': {
                    'title': _("Incorrect 'amount' value"),
                    'message':
                    _("The amount to pay for Voucher must be equal or \
                      less than the amount unreconciled"),
                },
            }

        if self.amount < 0:
            return {
                'warning': {
                    'title': _("Incorrect 'amount' value"),
                    'message':
                    _("The amount to pay for Voucher may not be negative"),
                },
            }
        return {}

    @api.onchange('reconcile')
    def _verify_full_reconcile2(self):
        if self.reconcile:
            self.amount = self.amount_unreconciled

    _sql_constraints = [
        ('amount_less_than_unreconciled',
         'CHECK(amount <= amount_unreconciled)',
         "The amount to pay for Voucher must be not greater \
                      than the amount unreconciled"),

        ('amount_greater than zero',
         'CHECK(amount >= 0)',
         "The amount to pay for Voucher may not be negative"),
    ]

    @api.constrains('date_original')
    def _check_date_less_than_payment_date(self):
        for rec in self:
            if rec.date_original and rec.date_original >\
                    rec.register_payment_id.date:
                raise exceptions.ValidationError(_(u"The vouchers to pay must be not later\
                than the payment"))
