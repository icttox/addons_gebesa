# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models


class AccountRegisterPaymentsLine(models.TransientModel):
    _inherit = 'account.register.payments.line'

    factoring_number = fields.Char(
        string=_("Factoring Number"),
        compute='_compute_factoring_number',
        store=True,
        readonly=True)

    @api.depends('invoice_id', 'invoice_id.factoring_customer_id',
                 'invoice_id.factoring_supplier_id',
                 'invoice_id.factoring_customer_id.consecutive',
                 'invoice_id.factoring_supplier_id.consecutive')
    def _compute_factoring_number(self):
        for line in self:
            factoring_number = False
            if line.invoice_id and line.invoice_id.factoring_customer_id and \
                    line.invoice_id.factoring_customer_id.consecutive:
                factoring_number = line.invoice_id.factoring_customer_id.consecutive
            if line.invoice_id and line.invoice_id.factoring_supplier_id and \
                    line.invoice_id.factoring_supplier_id.consecutive:
                factoring_number = line.invoice_id.factoring_supplier_id.consecutive
            line.factoring_number = factoring_number


class AccountPaymentLine(models.Model):
    _inherit = 'account.payment.line'

    factoring_number = fields.Char(
        string=_("Factoring Number"),
        compute='_compute_factoring_number',
        store=True,
        readonly=True)

    @api.depends('invoice_id', 'invoice_id.factoring_customer_id',
                 'invoice_id.factoring_supplier_id',
                 'invoice_id.factoring_customer_id.consecutive',
                 'invoice_id.factoring_supplier_id.consecutive')
    def _compute_factoring_number(self):
        for line in self:
            factoring_number = False
            if line.invoice_id and line.invoice_id.factoring_customer_id and \
                    line.invoice_id.factoring_customer_id.consecutive:
                factoring_number = line.invoice_id.factoring_customer_id.consecutive
            if line.invoice_id and line.invoice_id.factoring_supplier_id and \
                    line.invoice_id.factoring_supplier_id.consecutive:
                factoring_number = line.invoice_id.factoring_supplier_id.consecutive
            line.factoring_number = factoring_number
