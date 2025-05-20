# -*- coding: utf-8 -*-
# © <2016> <Cesar Barron Bautista>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError


class AccountPayment(models.Model):
    _name = "account.payment"
    _inherit = "account.payment"
    _description = "Payments"
    _order = "payment_date desc, name desc"

    register_line_ids = fields.One2many('account.payment.line',
                                        'payment_id',
                                        string="Invoices")

    @api.onchange('partner_type')
    def _onchange_partner_type(self):
        # Set partner_id domain
        if self.partner_type:
            return {'domain': {'partner_id': [(self.partner_type, '=', True),
                    ('parent_id', '=', False)]}}
        return {}

    def _get_liquidity_move_line_vals(self, amount):
        res = super()._get_liquidity_move_line_vals(amount)
        res.update({
            'analytic_account_id': self.account_analytic_id.id
        })
        return res

    def _create_payment_entry(self, amount):
        """ Create a journal entry corresponding to a payment, if the payment
            references invoice(s) they are reconciled.
            Return the journal entry.
        """
        if not self.register_line_ids and not self.register_line_ids.ids:
            res = super()._create_payment_entry(amount)
            return res

        aml_obj = self.env[
            'account.move.line'].with_context(check_move_validity=False)
        debit, credit, amount_currency, currency_id = \
            aml_obj.with_context(
                date=self.payment_date)._compute_amount_fields(
                    amount, self.currency_id, self.company_id.currency_id)
        credit = round(credit, 6)
        debit = round(debit, 6)
        amount_currency = round(amount_currency, 6)

        move = self.env['account.move'].create(self._get_move_vals())

        # Write line corresponding to invoice payment
        counterpart_aml_dict = self._get_multi_counterpart_move_line_vals(
            move.id)

        for aml_cont in counterpart_aml_dict:
            counterpart_aml = aml_obj.create(aml_cont)
            self.env['account.invoice'].browse(
                aml_cont['invoice_id']).register_payment(counterpart_aml)

        if credit > debit:
            total_payment = sum(move.line_ids.mapped('credit'))
            if abs(total_payment - credit) < 0.01:
                credit = total_payment
        else:
            total_payment = sum(move.line_ids.mapped('debit'))
            if abs(total_payment - debit) < 0.01:
                debit = total_payment

        # Write counterpart lines
        liquidity_aml_dict = self._get_shared_move_line_vals(
            credit, debit, -amount_currency, move.id, False)
        liquidity_aml_dict['currency_id'] = currency_id
        liquidity_aml_dict.update(self._get_liquidity_move_line_vals(-amount))
        aml_obj.create(liquidity_aml_dict)

        move.post()
        return move

    def _get_multi_counterpart_move_line_vals(self, move_id=False):
        aml_obj = self.env[
            'account.move.line'].with_context(check_move_validity=False)
        move_lines = []
        name = ''
        customer_pay = True
        if self.partner_type == 'customer':
            if self.payment_type == 'inbound':
                name += _(u"Customer Payment")
            elif self.payment_type == 'outbound':
                name += _(u"Customer Refund")
                customer_pay = False
        elif self.partner_type == 'supplier':
            if self.payment_type == 'inbound':
                name += _(u"Vendor Refund")
            elif self.payment_type == 'outbound':
                name += _(u"Vendor Payment")
                customer_pay = False

        for rec in self:
            aprl_ids = rec.register_line_ids
            for line in aprl_ids:
                name_line = name + ":" + line.invoice_id.number
                credit, debit, amount_currency, currency_id = \
                    aml_obj.with_context(
                        date=self.payment_date)._compute_amount_fields(
                            line.amount,
                            self.currency_id,
                            self.company_id.currency_id)
                credit = round(credit, 6)
                debit = round(debit, 6)
                amount_currency = round(amount_currency, 6)

                move_line = {
                    'partner_id': self.payment_type in
                    ('inbound', 'outbound') and
                    self.env['res.partner']._find_accounting_partner(
                        self.partner_id).id or False,
                    'invoice_id': line.invoice_id and
                    line.invoice_id.id or False,
                    'move_id': move_id,
                    'debit': debit if customer_pay else credit,
                    'credit': credit if customer_pay else debit,
                    'amount_currency': amount_currency or False,
                    'name': name_line,
                    'account_id': self.destination_account_id.id,
                    'journal_id': self.journal_id.id,
                    'currency_id': self.currency_id !=
                    self.company_id.currency_id and
                    currency_id or False,
                    'payment_id': self.id,
                    'analytic_account_id': line.invoice_id and
                    line.invoice_id.account_analytic_id and
                    line.invoice_id.account_analytic_id.id or False,
                }
                if move_line['credit'] > 0:
                    amount_currency = move_line['amount_currency'] * -1
                    move_line['amount_currency'] = amount_currency
                move_lines.append(move_line)
        return move_lines

    @api.multi
    def action_validate_invoice_payment(self):
        dif_date = any(
            self.payment_date < inv.date_invoice
            for inv in self.invoice_ids)
        if dif_date:
            raise UserError(
                "La fecha del pago no puede ser menor a la fecha de la factura")
        return super().action_validate_invoice_payment()

    @api.model
    def create(self, vals_list):
        if not self.env.user.has_group(
                'account_register_payments_line.group_account_register_payments_line_user'):
            raise UserError(
                "Usted no tiene privilegios para crear pagos")
        return super().create(vals_list)


class AccountPaymentLine(models.Model):
    _name = "account.payment.line"
    _description = "stores the invoices payed in this transaction and " \
        + "the amount payed to each one"

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
        'res.partner',
        string=_(u"Partner"),
        readonly=True,
        store=True)
    date_due = fields.Date(
        related='move_line_id.date_maturity',
        string=_(u"Due Date"),
        readonly=True,
        store=True)
    company_id = fields.Many2one(
        'res.company',
        string=_(u"Company"),
        store=True,
        readonly=True)
    amount_original = fields.Float(
        string=_(u"Original Amount"),
        store=True,
        digits=dp.get_precision('Account'))
    amount_unreconciled = fields.Float(
        string=_(u"Open Balance"),
        store=True,
        digits=dp.get_precision('Account'))
    currency_id = fields.Many2one(
        'res.currency',
        string=_(u"Currency"),
        readonly=True,
        store=True)
