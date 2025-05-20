# coding: utf-8
# Copyright 2016 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests.common import TransactionCase


class PointOfSale(TransactionCase):

    def setUp(self):
        super(PointOfSale, self).setUp()
        self.pos_order_obj = self.env['pos.order']
        self.pmp_obj = self.env['pos.make.payment']

        self.config = self.env.ref('point_of_sale.pos_config_main')
        self.partner = self.env.ref('base.res_partner_address_22')
        self.product = self.env.ref('product.product_product_9')
        self.action = self.env.ref(
            'l10n_mx_pos_cogs.automated_action_create_cogs_from_pos')
        self.session = self.env['pos.session'].create({
            'user_id': self.uid,
            'config_id': self.config.id
        })
        # Allowing Cancel Entries
        self.config.journal_id.update_posted = True

    def create_order(self, partner=False):
        """Create the orders needed for each use case"""
        taxes = self.env.ref('l10n_mx.1_tax12').ids
        taxes.extend(self.env.ref('l10n_mx.1_tax7').ids)
        # Creating Order
        order = self.pos_order_obj.create({
            'partner_id': partner or False,
            'session_id': self.session.id,
            'lines': [(0, 0, {
                'product_id': self.product.id,
                'price_unit': 100.0,
                'qty': 5.0,
                'tax_ids': [(6, 0, [taxes])],
            })]
        })
        # Executing the action server to simulate the real process
        action = self.action.with_context({
            'active_model': 'pos.order',
            '__action_done': {},
            'active_id': order.id,
            'active_ids': [order.id]})
        action._process(order)
        # Creating payment
        payment = self.pmp_obj.with_context(active_id=order.id).create({
            'journal_id': order.session_id.config_id.journal_ids.ids[0],
            'amount': order.amount_total
        })
        payment.check()
        return order

    def _check_cogs(self, order, ret=False):
        """Validate that all cogs were generated correctly with the order
        information"""
        # Getting the account to validate the corrects values for
        # debit and credit

        sacc = (
            self.product[ret and 'property_stock_account_input' or
                         'property_stock_account_output'].id or
            self.product.categ_id[
                ret and 'property_stock_account_input_categ_id' or
                'property_stock_account_output_categ_id'].id)
        eacc = (self.product.property_account_expense_id.id or
                self.product.categ_id.
                property_account_expense_categ_id.id)

        accounts = {
            sacc: ret and 'debit' or 'credit',
            eacc: ret and 'credit' or 'debit'
        }

        # Validate that the cogs was created correctly
        self.assertTrue(order.cogs_move_id,
                        'The Cost Journal Entry was not created')

        # Validating that the reference is correctly set
        self.assertEqual(order.name, order.cogs_move_id.ref,
                         'The ref of the Journal Entry is wrong')

        # Validating that the Partner is correctly set
        self.assertEqual(order.partner_id,
                         order.cogs_move_id.partner_id,
                         'The ref of the Journal Entry is wrong')

        values_in_line = [i.debit or i.credit
                          for i in order.cogs_move_id.line_ids]

        # Validating the values of credit and debit
        self.assertTrue(values_in_line.count(275) == 2,
                        'The values for debit and credit must be 275, '
                        'because the current cost for the product is 55')

        # Validating the state of the move created
        self.assertEqual(order.cogs_move_id.state, 'draft',
                         'The Journal Entry is not in draft state')
        # Checking that the credit and debit are correctly set
        for line in order.cogs_move_id.line_ids:
            self.assertEqual(275,
                             line[accounts.get(line.account_id.id)],
                             'The values of the credit and debit are not '
                             'correctly set in the Journal Entry for '
                             'the return')

    def test_01_cogs_in_pos(self):
        """Validate if the Cost Journal Entry is created correctly with the
        data extracted from pos order created previosly"""

        # Create an order without partner
        order = self.create_order()
        # Validating the Cost Journal Entry
        self._check_cogs(order)

        # Create an order with partner
        order = self.create_order(self.partner.id)
        # Validating the Cost Journal Entry
        self._check_cogs(order)

    def test_02_cogs_in_pos_with_invoice(self):
        """Validate if the Cost Journal Entry is removed correctly where the
        invoice for the pos order is created"""

        # Create an order with partner
        order = self.create_order(self.partner.id)
        # Validating the Cost Journal Entry
        self._check_cogs(order)
        # Creating Invoice
        order.action_pos_order_invoice()
        # Validating that the cogs was removed
        self.assertFalse(order.cogs_move_id,
                         'The Cost Journal Entry was not removed '
                         'when the invoice was created')

    def test_03_cogs_with_returns_without_invoice(self):
        """Validate how the cogs must be manage when there is return in a pos
        order without invoice in the process"""
        # Create an order with partner
        order = self.create_order(self.partner.id)
        # Validating the Cost Journal Entry
        self._check_cogs(order)
        refund = order.refund()
        # Validating if the refund was created
        self.assertTrue(refund.get('res_id'),
                        'The refund was not created')
        context = dict(refund.get('context', {}))
        # Creating the object for the return
        refund = self.pos_order_obj.browse(refund.get('res_id'))
        # Executing the action server to simulate the real process
        context.update({
            'active_model': 'pos.order',
            '__action_done': {},
            'active_id': refund.id,
            'active_ids': [refund.id]})

        action = self.action.with_context(context)
        action._process(refund)
        # Validating the Cost Journal Entry
        self._check_cogs(refund, True)

    def test_04_cogs_with_returns_with_invoice(self):
        """Validate how the cogs must be manage when there is return in a pos
        order wit invoice in the process"""
        # Create an order with partner
        order = self.create_order(self.partner.id)
        # Validating the Cost Journal Entry
        self._check_cogs(order)
        # Creating Invoice
        order.action_pos_order_invoice()
        # Validating that the cogs was removed
        self.assertFalse(order.cogs_move_id,
                         'The Cost Journal Entry was not removed '
                         'when the invoice was created')
        # Creating Refund
        refund = order.refund()
        # Validating if the refund was created
        self.assertTrue(refund.get('res_id'),
                        'The refund was not created')
        context = dict(refund.get('context', {}))
        # Creating the object for the return
        refund = self.pos_order_obj.browse(refund.get('res_id'))
        # Executing the action server to simulate the real process
        context.update({
            'active_model': 'pos.order',
            '__action_done': {},
            'active_id': refund.id,
            'active_ids': [refund.id]})

        action = self.action.with_context(context)
        action._process(refund)
        # Validating the Cost Journal Entry
        self.assertFalse(refund.cogs_move_id,
                         'The refund with invoice must not '
                         'have Cost Journal Entry')

    def test_05_close_open_invoices_in_session_close(self):
        """Close the current session and validate that the Journal Entry are
        correctly posted"""
        # Create an order with partner
        order = self.create_order()
        # Validating the Cost Journal Entry
        self._check_cogs(order)
        self.session.action_pos_session_closing_control()
        self.assertEqual(order.cogs_move_id.state,
                         'posted',
                         'The Journal Entry was not posted '
                         'when the session was closed')
