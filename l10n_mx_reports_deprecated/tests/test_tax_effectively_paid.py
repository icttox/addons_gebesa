# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _
from .common import MexicoReportsTestCase


class TaxEffectivelyPaid(MexicoReportsTestCase):
    def setUp(self):
        super(TaxEffectivelyPaid, self).setUp()
        self.payment_obj = self.env['account.payment']
        self.journal_payment = self.create_cash_journal()
        self.invoice_line_obj = self.env['account.invoice.line']
        self.tax_16 = self.env.ref('l10n_mx.1_tax12')
        self.journal_mx = self.env['account.journal'].search([
            ('name', '=', _('Customer Invoices'))], limit=1)
        self.payment_term_full = self.env.ref('account.account_payment_term')
        self.account_payment = self.env['res.partner.bank'].create({
            'acc_number': '123456789'})
        self.pay_method = self.env.ref(
            'account.account_payment_method_manual_out')
        self.uom_unit = self.env.ref('product.product_uom_unit')

    def test_001_tax_effectively_paid(self):
        """Verify that in tax movements are assigned the
        partner and invoice reference"""
        invoice = self.create_invoice()
        invoice.action_invoice_open()
        payment = self.payment_obj.create({
            'payment_date': invoice.date_invoice,
            'journal_id': self.journal_payment.id,
            'amount': invoice.amount_total,
            'invoice_ids': [(4, invoice.ids)],
            'payment_method_id': self.pay_method.id,
            'payment_type': 'inbound',
            'partner_id': invoice.partner_id.id,
            'partner_type': 'customer'})
        payment.post()
        move_tax = self.move_obj.search([
            ('partner_id', '=', invoice.partner_id.id),
            ('ref', '=', invoice.number),
            ('journal_id', '=', self.journal.id)], limit=1)
        self.assertTrue(move_tax.line_ids.filtered('partner_id').ids,
                        'Movement lines have not partner.')
        self.assertTrue(move_tax.line_ids.filtered('ref'),
                        'Movement lines have not invoice ref.')
        self.assertEquals(
            move_tax.ref, invoice.number, 'Not same ref and invoice number.')

    def create_invoice(self):
        invoice = self.invoice_obj.create({
            'partner_id': self.partner.id,
            'journal_id': self.journal_mx.id,
            'account_id': self.partner.property_account_receivable_id.id,
            'type': 'out_invoice',
            'payment_term_id': self.payment_term_full.id,
        })
        self.invoice_line_obj.create({
            'product_id': self.prod.id,
            'account_id': (self.prod.product_tmpl_id.
                           get_product_accounts().get('income').id),
            'quantity': 1,
            'price_unit': 100,
            'invoice_id': invoice.id,
            'uom_id': self.uom_unit.id,
            'name': 'Product that cost 100',
            'invoice_line_tax_ids': [(4, [self.tax_16.id, self.tax_ret.id])]
        })
        return invoice
