# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from calendar import monthrange
from dateutil.relativedelta import relativedelta
from .common import MexicoReportsTestCase


class AccountDiot(MexicoReportsTestCase):

    def setUp(self):
        super(AccountDiot, self).setUp()
        self.tax_obj = self.env['account.tax']
        self.invoice_obj = self.env['account.invoice']
        self.report_common = self.env['account.report.context.common']
        self.financial_export = self.env[
            'account.financial.html.report.xml.export']
        self.context_diot_obj = self.env['l10n_mx.account.context.diot']
        self.invoice_refund_obj = self.env['account.invoice.refund']

        self.tax16 = self.env.ref('l10n_mx.1_tax14')
        self.tax0 = self.env.ref('l10n_mx.1_tax13')
        self.tax_ret = self.env.ref('l10n_mx.1_tax7')
        self.tax_group = self.env.ref('l10n_mx.tax_group_iva')
        self.group_excempt = self.env.ref('l10n_mx.tax_group_iva_exent')
        self.account_type = self.env.ref(
            'account.data_account_type_current_assets')
        self.account = self.account_obj.create({
            'name': 'TAX TEST',
            'code': '1151003016',
            'user_type_id': self.account_type.id,
        })

        self.journal_payment = self.create_cash_journal()
        self.report_model = 'l10n_mx.account.diot'
        self.invoice_journal = self.journal_obj.create({
            'name': 'Supplier Invoice J',
            'type': 'purchase',
            'code': 'SUP',
        })
        self.vat = 'XXX010101XX1'
        self.p_name = 'Partner DIOT'
        self.partner.write({'vat': self.vat, 'name': self.p_name})

    def test_001_diot_without_moves(self):
        """Send to generate DIOT report without movements"""
        context_data = self.report_common.return_context(self.report_model, {})
        data = self.env[context_data[0]].browse(context_data[1]).get_xml()
        self.assertFalse(data, "File generated without documents.")

    def test_002_move_without_partner(self):
        """Create manually an move with DIOT data, but without partner."""
        move = self.move_obj.create({
            'name': 'Manually DIOT',
            'journal_id': self.journal.id,
            'date': self.date,
            'line_ids': [
                (0, 0, {
                    'name': 'Manually DIOT',
                    'journal_id': self.journal.id,
                    'account_id': self.account.id,
                    'debit': 100.0,
                    'tax_ids': [(6, 0, self.tax16.ids)]}),
                (0, 0, {
                    'name': 'Manually DIOT',
                    'journal_id': self.journal.id,
                    'account_id': self.account.id,
                    'credit': 100.0,
                }),
            ]})
        move.post()
        context_data = self.report_common.return_context(self.report_model, {})
        data = self.financial_export.browse().check_data_report(
            self.env[context_data[0]].browse(context_data[1]))
        self.assertEquals(
            data.get('name', ''), 'Moves without supplier',
            'View with movements without partner not returned.')

    def test_003_move_without_amount(self):
        """Create manually an move with DIOT data, but without amount base."""
        move = self.move_obj.create({
            'name': 'Manually DIOT',
            'journal_id': self.journal.id,
            'date': self.date,
            'partner_id': self.partner.id,
            'line_ids': [
                (0, 0, {
                    'name': 'Manually DIOT',
                    'partner_id': self.partner.id,
                    'journal_id': self.journal.id,
                    'account_id': self.account.id,
                    'debit': 0.0,
                    'tax_ids': [(6, 0, self.tax16.ids)]}),
                (0, 0, {
                    'name': 'Manually DIOT',
                    'partner_id': self.partner.id,
                    'journal_id': self.journal.id,
                    'account_id': self.account.id,
                    'credit': 0.0,
                }),
            ]})
        move.post()
        context_data = self.report_common.return_context(self.report_model, {})
        ctx = self.context_diot_obj.browse(context_data[1])
        ctx.unfolded_partners = self.partner
        data = self.financial_export.browse().check_data_report(
            self.env[context_data[0]].browse(context_data[1]))
        self.assertFalse(
            data, 'Movements were thout amount base not omitted in the report')

    def test_004_move_partner_without_data(self):
        """Generate movement to report in DIOT, but the partner without
        DIOT data required."""
        self.partner.country_id = False
        self.generate_invoice(self.tax16)
        context_data = self.report_common.return_context(self.report_model, {})
        data = self.financial_export.browse().check_data_report(
            self.env[context_data[0]].browse(context_data[1]))
        self.assertEquals(
            data.get('name', ''),
            'Suppliers without information necessary for DIOT',
            'View with suppliers without DIOT information not returned.')

    def test_005_generate_diot_16(self):
        """Generated a move with tax 16%, is generated DIOT Report"""
        self.generate_invoice(self.tax16)
        context_data = self.report_common.return_context(self.report_model, {})
        data = self.env[context_data[0]].browse(context_data[1]).get_xml()
        self.assertEquals(
            data, '04|85|%s|||||100|||||||||||||||\n' % (self.vat))

    def test_006_generate_diot_0(self):
        """Generated a move with tax 0%, is generated DIOT Report"""
        self.generate_invoice(self.tax0)
        context_data = self.report_common.return_context(self.report_model, {})
        data = self.env[context_data[0]].browse(context_data[1]).get_xml()
        self.assertEquals(
            data, '04|85|%s||||||||||||||||100||||\n' % (self.vat))

    def test_007_generate_diot_ret(self):
        """Generated a move with retention tax 10.67%, verify that is generated
        DIOT Report"""
        self.generate_invoice(self.tax_ret)
        context_data = self.report_common.return_context(self.report_model, {})
        data = self.env[context_data[0]].browse(context_data[1]).get_xml()
        self.assertEquals(
            data, '04|85|%s||||||||||||||||||11||\n' % (self.vat))

    def test_008_generate_diot_excempt(self):
        """Generated a move with tax 0% Excempt, verify that is generated DIOT
        Report"""
        tax = self.create_tax(0.0)
        tax.write({'tax_group_id': self.group_excempt.id})
        self.generate_invoice(tax)
        context_data = self.report_common.return_context(self.report_model, {})
        data = self.env[context_data[0]].browse(context_data[1]).get_xml()
        self.assertEquals(
            data, '04|85|%s|||||||||||||||||100|||\n' % (self.vat))

    def test_009_generate_diot_two_moves(self):
        """Generated two movements to tax 16%, and verify that amount is the
        sum of two movements"""
        self.generate_invoice(self.tax16)
        self.generate_invoice(self.tax16)
        context_data = self.report_common.return_context(self.report_model, {})
        data = self.env[context_data[0]].browse(context_data[1]).get_xml()
        self.assertEquals(
            data, '04|85|%s|||||200|||||||||||||||\n' % (self.vat))

    def test_010_generate_diot_foreign_supplier(self):
        """Generated two movements to tax 16%, this movement is to Foreign
        Supplier."""
        self.partner.write({
            'country_id': self.country_usa.id,
        })
        self.generate_invoice(self.tax16)
        context_data = self.report_common.return_context(self.report_model, {})
        data = self.env[context_data[0]].browse(context_data[1]).get_xml()
        self.assertEquals(
            data, '05|85||%s|%s|US|Americano|100|||||||||||||||\n' % (
                self.vat, self.p_name), 'File generated with other values.')

    def test_011_generate_diot_refund_paid(self):
        """Verify that with invoice refund is not generated DIOT report."""
        invoice = self.generate_invoice(self.tax16)
        refund = self.invoice_refund_obj.with_context(
            active_ids=invoice.ids).create({
                'filter_refund': 'refund',
                'description': 'Refund Test',
                'date_invoice': invoice.date_invoice,
            })
        result = refund.invoice_refund()
        refund_id = result.get('domain')[1][2]
        refund = self.invoice_obj.browse(refund_id)
        refund.action_invoice_open()
        refund.pay_and_reconcile(
            self.journal_payment, pay_amount=invoice.amount_total,
            date=invoice.date_invoice)
        context_data = self.report_common.return_context(self.report_model, {})
        data = self.env[context_data[0]].browse(context_data[1]).get_xml()
        self.assertFalse(data, "File generated to invoice refund.")

    def test_012_generate_diot_refund_not_paid(self):
        """Verify that with invoice refund not paid, is not generated DIOT
        report."""
        invoice = self.generate_invoice(self.tax16, pay=False)
        self.invoice_refund_obj.with_context(active_ids=invoice.ids).create({
            'filter_refund': 'cancel',
            'description': 'Refund Test',
            'date_invoice': invoice.date_invoice,
        }).invoice_refund()
        context_data = self.report_common.return_context(self.report_model, {})
        data = self.env[context_data[0]].browse(context_data[1]).get_xml()
        self.assertFalse(data, "File generated to invoice refund.")

    def test_013_generate_diot_16_last_month(self):
        """Generated a invoice to last month with tax 16%"""
        self.date = self.date - relativedelta(months=1)
        self.generate_invoice(self.tax16)
        context_data = self.report_common.return_context(self.report_model, {})
        data = self.env[context_data[0]].browse(context_data[1])
        self.assertFalse(data.get_xml())
        last_month_day = monthrange(self.date.year, self.date.month)[1]
        data = self.env[context_data[0]].browse(context_data[1])
        data.date_from = self.date.replace(day=1).strftime('%Y-%m-%d')
        data.date_to = self.date.replace(
            day=last_month_day).strftime('%Y-%m-%d')
        data = data.get_xml()
        self.assertEquals(
            data, '04|85|%s|||||100|||||||||||||||\n' % (self.vat))

    def generate_invoice(self, tax, pay=True):
        invoice = self.invoice_obj.create({
            'partner_id': self.partner.id,
            'type': 'in_invoice',
            'date_invoice': self.date.replace(day=15),
            'account_id': self.partner.property_account_payable_id.id,
            'journal_id': self.invoice_journal.id,
        })
        self.env['account.invoice.line'].create({
            'product_id': self.prod.id,
            'account_id': (self.prod.product_tmpl_id.
                           get_product_accounts().get('income').id),
            'quantity': 1,
            'price_unit': 100,
            'name': 'Product Test',
            'invoice_id': invoice.id,
            'invoice_line_tax_ids': [(4, tax.ids)]
        })
        invoice.compute_taxes()
        invoice.action_invoice_open()
        if pay:
            invoice.pay_and_reconcile(
                self.journal_payment, pay_amount=invoice.amount_total,
                date=self.date.replace(day=15))
        return invoice

    def create_tax(self, amount):
        return self.tax_obj.create({
            'name': 'TAX TEST',
            'type_tax_use': 'purchase',
            'amount_type': 'percent',
            'amount': amount,
            'tax_group_id': self.tax_group.id,
            'use_cash_basis': True,
            'cash_basis_account_id': self.account.id,
        })
