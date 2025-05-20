# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    prepayment_type = fields.Selection(
        [('normal', 'Normal'),
         ('advance', 'Advance')],
        string='Prepayment Type',
        default='normal'
    )

    pending_amount = fields.Float(
        'Pending Amount',
        digits=dp.get_precision('Account'),
    )

    account_analytic_id = fields.Many2one(
        'account.analytic.account',
        string='Analytic Account',
    )

    responsible_id = fields.Many2one(
        'hr.employee',
        string='Responsible Advance',
    )

    due_date_advance = fields.Date(
        string='Fecha Vencimiento Anticipo',
    )
    reconcile_advance_ids = fields.Many2many(
        'gebesa.reconcile.advance',
        string='Conciliaciones de anticipo',
        copy=False,
    )

    @api.one
    @api.depends('invoice_ids', 'payment_type', 'partner_type', 'partner_id',
                 'prepayment_type')
    def _compute_destination_account_id(self):
        super()._compute_destination_account_id()
        if self.prepayment_type == 'advance':
            if self.partner_id:
                if self.partner_type == 'customer':
                    # Dec 2017 cfdi 3.3 does not allow this type of advance
                    today = fields.Datetime.now()
                    # if today >= '2018-01-01 00:06:00':
                    #     raise exceptions.ValidationError(
                    #         "Due new regulations in CFDi 3.3"
                    #         " this operation is not longer allowed,"
                    #         " instead you must create an invoice for advance"
                    #         " please...")
                    self.destination_account_id = self.partner_id.\
                        property_account_customer_advance_id.id
                else:
                    self.destination_account_id = self.partner_id.\
                        property_account_supplier_advance_id.id

    def _create_payment_entry(self, amount):
        """ Create a journal entry corresponding to a payment, if the payment
            references invoice(s) they are reconciled.
            Return the journal entry.
        """
        if self.prepayment_type != 'advance':
            move = super()._create_payment_entry(amount)
        else:
            aml_obj = self.env['account.move.line'].with_context(
                check_move_validity=False)
            debit, credit, amount_currency, currency_id = aml_obj.with_context(
                date=self.payment_date)._compute_amount_fields(
                amount, self.currency_id, self.company_id.currency_id)

            move = self.env['account.move'].create(self._get_move_vals())

            diff = amount_currency
            diff_debit = debit
            diff_credit = credit

            # Write line corresponding to advance
            if self.partner_type == 'customer':
                if self.partner_id.country_id.code == "MX":
                    advance_tax_id = self.company_id.advance_tax_cust_id
                    if not advance_tax_id:
                        raise ValidationError('Favor de configurar los impuestos de anticipo por default en la compañía.')
                    porcentaje = advance_tax_id.amount / 100
                    cta_cont = advance_tax_id.cash_basis_account_id.id
                    if not cta_cont:
                        raise ValidationError('El impuesto para anticipos configurados en la compañía no tienen una cuenta de impuesto recibido.')
                    cta_cont2 = advance_tax_id.account_id.id
                    if not cta_cont:
                        raise ValidationError('El impuesto para anticipos configurados en la compañía no tienen una cuenta contable.')
                    # diff = round(diff / (1 + porcentaje), 6)
                    diff_tax = round(porcentaje * (diff / (1 + porcentaje)), 6)
                    # diff_debit = round(diff_debit / (1 + porcentaje), 6)
                    diff_debit_tax = round(porcentaje * (diff_debit / (1 + porcentaje)), 6)
                    # diff_credit = round(diff_credit / (1 + porcentaje), 6)
                    diff_credit_tax = round(porcentaje * (diff_credit / (1 + porcentaje)), 6)
                    counterpart_aml_tax_dict = self._get_shared_move_line_vals(
                        diff_debit_tax, diff_credit_tax, diff_tax,
                        move.id, False)
                    if not advance_tax_id.name:
                        raise ValidationError('El impuesto para anticipos configurados en la compañía no tiene un nombre.')
                    counterpart_aml_tax_dict.update({
                        'name': advance_tax_id.name,
                        'account_id': cta_cont,
                        'journal_id': self.journal_id.id,
                        'currency_id': self.currency_id != self.company_id.currency_id and self.currency_id.id or False,
                        'payment_id': self.id
                    })
                    aml_obj.create(counterpart_aml_tax_dict)
                    counterpart_aml_tax_dict2 = self._get_shared_move_line_vals(
                        diff_credit_tax, diff_debit_tax, diff_tax * -1,
                        move.id, False)
                    counterpart_aml_tax_dict2.update({
                        'name': advance_tax_id.name,
                        'account_id': cta_cont2,
                        'journal_id': self.journal_id.id,
                        'currency_id': self.currency_id != self.company_id.currency_id and self.currency_id.id or False,
                        'payment_id': self.id
                    })
                    aml_obj.create(counterpart_aml_tax_dict2)
            counterpart_aml_dict = self._get_shared_move_line_vals(
                diff_debit, diff_credit, diff, move.id, False)
            counterpart_aml_dict.update(self._get_counterpart_move_line_vals(
                self.invoice_ids))
            counterpart_aml_dict.update({'currency_id': self.currency_id !=
                                         self.company_id.currency_id and
                                         self.currency_id.id or False})

            counterpart_aml = aml_obj.create(counterpart_aml_dict)

            # Reconcile with the invoices
            if self.payment_difference_handling == 'reconcile':
                self.invoice_ids.register_payment(
                    counterpart_aml, self.writeoff_account_id, self.journal_id)
            else:
                self.invoice_ids.register_payment(counterpart_aml)

            # Write counterpart lines
            liquidity_aml_dict = self._get_shared_move_line_vals(
                credit, debit, -amount_currency, move.id, False)
            liquidity_aml_dict.update(
                self._get_liquidity_move_line_vals(-amount))
            aml_obj.create(liquidity_aml_dict)

            move.post()
        return move

    @api.multi
    def post(self):
        res = super().post()
        for rec in self:
            if rec.prepayment_type == 'advance':
                self.write({'pending_amount': rec.amount})
            else:
                self.write({'pending_amount': 0.0})
            return res

    @api.multi
    def cancel(self):
        for pay in self:
            if pay.reconcile_advance_ids:
                raise UserError("El anticipo %s ya esta conciliado" % pay.name)
        return super().cancel()
