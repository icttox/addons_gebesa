# -*- coding: utf-8 -*-
# © <2016> <Cesar Barron Bautista>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, exceptions, fields, models
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError


class AccountRegisterPayments(models.TransientModel):
    _name = 'account.register.payments'
    _inherit = 'account.register.payments'

    line_ids = fields.One2many('account.register.payments.line',
                               'register_payment_id',
                               string=_(u"Invoices"))
    group_invoices = fields.Boolean(
        string="Group Invoices",
        default=True,
        help="""If enabled, groups invoices by commercial partner, invoice account,
            type and recipient bank account in the generated payments. If disabled,
            a distinct payment will be generated for each invoice.""")
    account_analytic_id = fields.Many2one(
        'account.analytic.account',
        string=_('Analytic Account'),
    )

    @api.constrains('amount')
    def _check_total_mustbe_sum_of_lines(self):
        for rec in self:
            if rec.line_ids:
                total_amount_lines = 0.00
                for line in rec.line_ids:
                    total_amount_lines += line.amount
                difference = self.amount - total_amount_lines
                if abs(difference) > 0.05:
                    raise exceptions.ValidationError(_(u"The sum of the amount to \
                                                     pay per invoice '%d'\
                                                     must be equal than \
                                                     the payment amount '%s'")
                                                     % (total_amount_lines,
                                                        self.amount))

    def _prepare_payment_vals(self, invoices):
        """ Hook for extension """
        res = super()._prepare_payment_vals(invoices)
        lines = []
        for line in self.line_ids:
            account_type = False
            if line.invoice_id.type == 'out_invoice':
                account_type = 'receivable'
            elif line.invoice_id.type == 'in_invoice':
                account_type = 'payable'
            aml_ids = self.env[
                'account.move.line'].search(
                    [('account_id.internal_type', '=', account_type),
                     ('full_reconcile_id', '=', False),
                     ('move_id', '=', line.invoice_id.move_id.id)],
                    limit=1, order='date_maturity')
            aprl = {
                'invoice_id': line.invoice_id.id,
                'name': line.invoice_id.name,
                'account_id': line.account_id.id,
                'untax_amount': line.untax_amount,
                'amount': line.amount,
                'reconcile': line.reconcile,
                'account_analytic_id': line.account_analytic_id.id,
                'move_line_id': aml_ids[0].id,
                'date_original': line.invoice_id.date_invoice,
                'origin': line.invoice_id.origin,
                'reference': line.invoice_id.reference,
                'partner_id': line.partner_id.id,
                'date_due': line.invoice_id.date_due,
                'company_id': line.invoice_id.company_id.id,
                'amount_original': line.invoice_id.amount_total,
                'amount_unreconciled': line.invoice_id.residual,
                'currency_id': line.currency_id.id
            }
            lines.append([0, False, aprl])
        res.update({
            'account_analytic_id': self.account_analytic_id.id,
            'register_line_ids': lines,
        })
        return res

    @api.model
    def default_get(self, fields):
        rec = super().default_get(fields)
        context = dict(self._context or {})
        active_model = context.get('active_model')
        active_ids = context.get('active_ids')

        # Checks on context parameters
        if not active_model or not active_ids:
            raise UserError(_(u"Programmation error: \
                            wizard action executed without active_model \
                            or active_ids in context."))
        if active_model != 'account.invoice':
            raise UserError(_(u"Programmation error: the expected model \
                            for this action is 'account.invoice'. \
                            The provided one is '%d'.") % active_model)

        # Checks on received invoice records
        invoices = self.env[active_model].browse(active_ids)
        lines = []
        aml_ids = False
        account_type = False
        if any(invoice.type == 'out_invoice' for invoice in invoices):
            account_type = 'receivable'
        elif any(invoice.type == 'in_invoice' for invoice in invoices):
            account_type = 'payable'

        # Fill the defaults values of the selected invoices
        for inv in invoices:
            aml_ids = self.env[
                'account.move.line'].search([
                                            ('account_id.internal_type', '=',
                                             account_type),
                                            ('full_reconcile_id', '=', False),
                                            ('move_id', '=', inv.move_id.id)],
                                            limit=1,
                                            order='date_maturity')
            if not aml_ids:
                raise UserError(
                    "Error de configuración del proveedor, la factura no "
                    "contiene una cuenta contable a pagar o a cobrar...")
            account_id = aml_ids[0].account_id.id
            analytic_id = aml_ids[0].analytic_account_id.id
            aprl = {
                'move_line_id': aml_ids[0].id,
                'account_id': account_id,
                'untax_amount': inv.amount_untaxed,
                'amount': inv.residual,
                'name': inv.name,
                'origin': inv.origin,
                'reference': inv.reference,
                'reconcile': True,
                'account_analytic_id': analytic_id,
                'date_original': inv.date_invoice,
                'partner_id': inv.partner_id.id,
                'date_due': inv.date_due,
                'company_id': inv.company_id.id,
                'amount_original': inv.amount_total,
                'amount_unreconciled': inv.residual,
                'currency_id': inv.currency_id.id,
                'invoice_id': inv.id,
                'register_payment_id': self.id
            }
            lines.append([0, False, aprl])
        rec.update({
            'line_ids': lines,
        })
        return rec

    @api.multi
    def create_payments(self):
        diff_partner_bank = any(
            inv.partner_bank_id != self.invoice_ids[0].partner_bank_id
            for inv in self.invoice_ids)
        if diff_partner_bank:
            raise UserError(
                "Las cuentas bancarias de las facturas son diferentes")
        diff_date_inv = any(
            self.payment_date < inv.date_invoice
            for inv in self.invoice_ids)
        if diff_date_inv:
            raise UserError(
                "La fecha del pago no puede ser menor a la fecha de las factura(s)")
        return super().create_payments()


class AccountRegisterPaymentsLine(models.TransientModel):
    _name = 'account.register.payments.line'
    _description = "stores the invoices payed in this transaction and " \
        + "the amount payed to each one"

    register_payment_id = fields.Many2one(
        'account.register.payments',
        string=_(u"Register payment"),
        required=True,
        ondelete='cascade')
    payment_id = fields.Many2one(
        'account.payment',
        string=_(u"Payment"),
        required=False)
    invoice_id = fields.Many2one(
        'account.invoice',
        string=_(u"Invoice"),
        required=False)
    account_id = fields.Many2one(
        'account.account',
        string=_(u"Account"),
        required=True)
    untax_amount = fields.Float(string=_(u"Untax Amount"))
    amount = fields.Float(
        string=_(u"Amount"),
        digits=dp.get_precision('Account'))
    reconcile = fields.Boolean(string=_(u"Full Reconcile"))
    account_analytic_id = fields.Many2one(
        'account.analytic.account',
        string=_(u"Analytic Account"))
    move_line_id = fields.Many2one(
        'account.move.line',
        string=_(u"Journal Item"),
        copy=False)
    date_original = fields.Date(
        related='move_line_id.date',
        string=_(u"Date"),
        readonly=True,
        store=True)
    name = fields.Char(
        string=_(u"Reference/Description"),
        readonly=True)
    origin = fields.Char(
        string=_(u"Source Document"),
        readonly=True)
    reference = fields.Char(
        string=_(u"Vendor Reference"),
        readonly=True)
    partner_id = fields.Many2one(
        related='register_payment_id.partner_id',
        string=_(u"Partner"),
        readonly=True,
        store=True)
    date_due = fields.Date(
        related='move_line_id.date_maturity',
        string=_(u"Due Date"),
        readonly=True,
        store=True)
    # company_id = fields.Many2one(
    #     related='register_payment_id.company_id',
    #     string=_(u"Company"),
    #     store=True,
    #     readonly=True)
    amount_original = fields.Float(
        string=_(u"Original Amount"),
        store=True,
        digits=dp.get_precision('Account'))
    amount_unreconciled = fields.Float(
        string=_(u"Open Balance"),
        store=True,
        digits=dp.get_precision('Account'))
    currency_id = fields.Many2one(
        related='register_payment_id.currency_id',
        string=_(u"Currency"),
        readonly=True,
        store=True)

    @api.onchange('amount')
    def _verify_full_reconcile(self):
        if self.amount == self.amount_unreconciled:
            self.reconcile = True
        else:
            self.reconcile = False

        if self.amount > self.amount_unreconciled:
            return {
                'warning': {
                    'title': _(u"Incorrect 'amount' value"),
                    'message':
                    _(u"The amount to pay for Invoice must be equal or \
                      less than the amount unreconciled"),
                },
            }

        if self.amount < 0:
            return {
                'warning': {
                    'title': _(u"Incorrect 'amount' value"),
                    'message':
                    _(u"The amount to pay for Invoice may not be negative"),
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
         "The amount to pay for Invoice must be not greater \
                      than the amount unreconciled"),

        ('amount_greater than zero',
         'CHECK(amount >= 0)',
         "The amount to pay for Invoice may not be negative"),
    ]

    @api.constrains('date_original')
    def _check_date_less_than_payment_date(self):
        for rec in self:
            if rec.date_original and rec.date_original >\
                    rec.register_payment_id.payment_date:
                raise exceptions.ValidationError(_(u"The invoices to pay must be not later\
                than the payment"))
