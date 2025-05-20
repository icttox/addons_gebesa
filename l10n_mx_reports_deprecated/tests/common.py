# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields
from odoo.tests.common import TransactionCase


class MexicoReportsTestCase(TransactionCase):

    def setUp(self):
        super(MexicoReportsTestCase, self).setUp()
        self.move_obj = self.env['account.move']
        self.journal_obj = self.env['account.journal']
        self.account_obj = self.env['account.account']
        self.tax_obj = self.env['account.tax']
        self.report_common = self.env['account.report.context.common']
        self.financial_export = self.env[
            'account.financial.html.report.xml.export']
        self.partner = self.env.ref('base.res_partner_12')
        self.country_mx = self.env.ref('base.mx')
        self.country_usa = self.env.ref('base.us')
        self.company = self.env.ref('base.main_company')
        self.invoice_obj = self.env['account.invoice']
        self.account_type_cash = self.env.ref(
            'account.data_account_type_liquidity')
        self.prod = self.env.ref('product.product_product_8')
        self.tax_ret = self.env.ref('l10n_mx.1_tax7')
        self.journal = self.create_journal_basis()
        self.date = fields.Datetime.context_timestamp(
            self.journal, fields.Datetime.from_string(
                fields.Datetime.now()))

    def create_cash_journal(self):
        account_cash = self.account_obj.create({
            'name': 'Cash',
            'code': '11111101',
            'user_type_id': self.account_type_cash.id,
        })
        return self.journal_obj.create({
            'name': 'Cash',
            'type': 'cash',
            'code': 'Cash',
            'default_debit_account_id': account_cash.id,
            'default_credit_account_id': account_cash.id
        })

    def create_journal_basis(self):
        journal = self.journal_obj.create({
            'name': 'Efectivamente Pagado',
            'type': 'general',
            'code': 'EP',
        })
        self.company.write({
            'tax_cash_basis_journal_id': journal.id,
        })
        return journal
