# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import date, timedelta
from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError


class TestDaysTolerance(TransactionCase):

    def setUp(self, *args, **kwargs):
        super(TestDaysTolerance, self).setUp(*args, **kwargs)
        self.account_invoice_obj = self.env['account.invoice']
        self.res_users_obj = self.env['res.users']
        self.account_obj = self.env['account.account']
        self.employee_obj = self.env['hr.employee']
        self.payments_obj = self.env['account.register.payments'].with_context(
            active_model='account.invoice')

        res_users_account_manager = self.env.ref(
            'account.group_account_manager')
        partner_manager = self.env.ref('base.group_partner_manager')

        self.user_day_tolerance = self.res_users_obj.with_context(
            {'no_reset_password': True}).create(dict(
                name="Days Tolerance",
                company_id=self.env.ref('base.main_company').id,
                login="Days",
                email="days_tolerance@yourcompany.com",
                groups_id=[(
                    6, 0, [res_users_account_manager.id, partner_manager.id])]
            ))

    def test_invoice_days_tolerance(self):
        payment_term = self.env.ref(
            'account.account_payment_term_advance')
        journalrec = self.env['account.journal'].search(
            [('type', '=', 'sale')])[0]
        partner3 = self.env.ref('base.res_partner_3')
        account_user_type = self.env.ref(
            'account.data_account_type_receivable')
        payment_method_manual_in = self.env.ref(
            "account.account_payment_method_manual_in")
        bank_journal_euro = self.env['account.journal'].create(
            {'name': 'Bank', 'type': 'bank', 'code': 'BNK67'})

        account_rec1_id = self.account_obj.sudo(
            self.user_day_tolerance.id).create(dict(
                code="cust_acc",
                name="customer account",
                user_type_id=account_user_type.id,
                reconcile=True,
            ))

        invoice_line_data = [
            (0, 0, {
                'product_id': self.env.ref('product.product_product_5').id,
                'quantity': 10.0,
                'account_id': self.env['account.account'].search(
                    [('user_type_id', '=', self.env.ref(
                        'account.data_account_type_revenue').id)], limit=1).id,
                'name': 'product test 5',
                'price_unit': 100.00,
            })
        ]

        date_invoice = date.today() - timedelta(days=5)

        invoice_day_tolerance = self.account_invoice_obj.sudo(
            self.user_day_tolerance.id).create(dict(
                name="Test Customer Invoice Days Tolerance",
                payment_term_id=payment_term.id,
                journal_id=journalrec.id,
                partner_id=partner3.id,
                account_id=account_rec1_id.id,
                invoice_line_ids=invoice_line_data,
                date_invoice=date_invoice
            ))

        with self.assertRaises(UserError, msg="You do not have an assigned employee.\n Please \
                contact your system administrator"):
            invoice_day_tolerance.action_invoice_open()

        employee_day_tolerance = self.employee_obj.create(dict(
            name='Days Tolerance',
            user_id=self.user_day_tolerance.id,
            tolerance_days=1
        ))

        with self.assertRaises(UserError, msg="You can not bill! \
                The date may not be earlier \
                than %s ."):
            invoice_day_tolerance.action_invoice_open()

        employee_day_tolerance.tolerance_days = 10

        # I validate invoice by creating on
        invoice_day_tolerance.action_invoice_open()

        # I check that the invoice state is "Open"
        self.assertEquals(invoice_day_tolerance.state, 'open')

        ctx = {
            'active_model': 'account.invoice',
            'active_ids': [invoice_day_tolerance.id]}
        register_payments = self.payments_obj.with_context(
            ctx).sudo(self.user_day_tolerance.id).create({
                'payment_date': date_invoice,
                'journal_id': bank_journal_euro.id,
                'payment_method_id': payment_method_manual_in.id,
                'group_invoices': False,
            })
        employee_day_tolerance.user_id = False

        with self.assertRaises(UserError, msg="You do not have an assigned employee.\n Please \
                contact your system administrator"):
            register_payments.create_payments()

        employee_day_tolerance.write(dict(
            user_id=self.user_day_tolerance.id,
            tolerance_days=1
        ))

        with self.assertRaises(UserError, msg="Error! \
                The date may not be earlier \
                than %s ."):
            register_payments.create_payments()

        employee_day_tolerance.write(dict(
            tolerance_days=10
        ))
        register_payments.create_payments()
