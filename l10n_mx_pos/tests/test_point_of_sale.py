# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger
from odoo import fields


class PointOfSale(TransactionCase):

    def setUp(self):
        super(PointOfSale, self).setUp()
        self.pos_order_obj = self.env['pos.order']
        self.pmp_obj = self.env['pos.make.payment']
        self.payment = self.env['account.register.payments']
        self.att_obj = self.env['ir.attachment']

        self.partner1 = self.env.ref(
            'l10n_mx_base.res_partner_address_vauxoo_1')
        self.partner2 = self.env.ref('base.res_partner_address_22')
        self.uid = self.env['res.users'].create({
            'name': 'Pos User',
            'login': 'pos_user',
            'email': 'pos_user@yourcompany.com',
            'company_id': self.env.ref('base.main_company').id,
            'groups_id': [(6, 0, [self.ref('point_of_sale.group_pos_user'),
                                  self.ref('base.group_user'),
                                  self.ref('sales_team.group_sale_salesman'),
                                  self.ref('account.group_account_invoice'),
                                  ])]
        }).id
        self.product = self.env.ref('product.product_product_8')
        self.session = self.env['pos.session'].with_env(
            self.env(user=self.uid)).create(
                {'user_id': self.uid,
                 'config_id': self.env.ref('point_of_sale.pos_config_main').id
                 })
        self.pac = self.env.ref('l10n_mx_base.pac_vauxoo')
        self.session.config_id.journal_id.sequence_id.write({
            'prefix': 'POS',
            'suffix': '',
            'pac_id': self.pac.id})
        self.partner2.commercial_partner_id.vat = False
        self.partner1.l10n_mx_payment_method_id = self.env.ref(
            'l10n_mx_base.payment_method_otros')

    def test_001_pos_not_invoiced(self):
        """Create order with all data to invoice.
        In this case, the order created have all information to generate the
        invoice, but is not generated from PoS.
        Verify that the order is invoiced with the Odoo process, the session
        must not have XML attached."""
        self.create_order(self.partner1.id)
        self.session.create_xml_session()
        self.assertFalse(
            self.att_obj.search([
                ('res_model', '=', 'pos.session'),
                ('res_id', '=', self.session.id)]), 'Attachments generated')

    def test_002_pos_partner(self):
        """Generated order with partner, but address is incomplete.
        Is created the order with partner, but the partner have not RFC.
        The session must have one XML attached and one PDF"""
        self.create_order(self.partner2.id)
        self.session.create_xml_session()
        self.assertEquals(
            len(self.att_obj.search([
                ('res_model', '=', 'pos.session'),
                ('res_id', '=', self.session.id)]).ids), 2,
            'Attachments not generated')

    def test_003_pos_witout_partner(self):
        """Generated the order without partner.
        The session must have one XML attached and one PDF"""
        self.create_order()
        self.session.create_xml_session()
        self.assertEquals(
            len(self.att_obj.search([
                ('res_model', '=', 'pos.session'),
                ('res_id', '=', self.session.id)]).ids), 2,
            'Attachments not generated')

    def test_004_pos_all_cases(self):
        """Generated the order without partner, with partner and without RFC in
        partner.
        The session must have two XML attached and two PDF"""
        self.create_order()
        self.create_order(self.partner1.id)
        self.create_order(self.partner2.id)
        self.session.create_xml_session()
        self.assertEquals(
            len(self.att_obj.search([
                ('res_model', '=', 'pos.session'),
                ('res_id', '=', self.session.id)]).ids), 4,
            'Attachments not generated')

    def test_005_pos_error_stamp(self):
        """Try send to stamp the XML without PAC configured."""
        self.session.config_id.journal_id.sequence_id.write({
            'pac_id': False})
        self.create_order(self.partner2.id)
        with mute_logger('odoo.addons.l10n_mx_pos.models.point_of_sale'):
            self.session.create_xml_session()
        att = self.att_obj.search([
            ('res_model', '=', 'pos.session'),
            ('res_id', '=', self.session.id)])
        self.assertTrue(
            att.filtered(lambda r: '.log' in r.datas_fname),
            'Attachment with error message not generated.')

    def test_006_generate_xml_several_times(self):
        """Send to generate several times the XML, only the first time must
        generate the XML and PDF."""
        self.create_order(self.partner2.id)
        self.session.create_xml_session()
        self.session.create_xml_session()
        self.assertEquals(
            len(self.att_obj.search([
                ('res_model', '=', 'pos.session'),
                ('res_id', '=', self.session.id)]).ids), 2,
            'Attachments generated several times')

    def test_007_pos_validate_invoice(self):
        """Verify that invoice is generated automatically when is created the
        order, without generate the invoice from PoS."""
        self.create_order(self.partner1.id)
        self.session.create_xml_session()
        order = self.session.order_ids
        self.assertTrue(
            order.invoice_id, 'Invoice not validated')

    def test_008_pos_two_orders_by_case(self):
        """Generated two orders without partner, with partner and without
        complete address.
        The session must generate only one attachment by case."""
        self.create_order()
        self.create_order(self.partner1.id)
        self.create_order(self.partner2.id)
        self.create_order()
        self.create_order(self.partner1.id)
        self.create_order(self.partner2.id)
        self.session.create_xml_session()
        self.assertEquals(
            len(self.att_obj.search([
                ('res_model', '=', 'pos.session'),
                ('res_id', '=', self.session.id)]).ids), 4,
            'Attachments not generated')

    def test_009_delete_attachment(self):
        """Try delete XML and PDF attachment from the sesion"""
        self.create_order(self.partner2.id)
        self.session.create_xml_session()
        with self.assertRaisesRegexp(
                ValidationError,
                'You cannot delete an set of documents which has a legal'):
            self.env['ir.attachment'].search([
                ('res_id', '=', self.session.id),
                ('mimetype', 'in', ('application/pdf', 'application/xml')),
                ('name', 'ilike', self.session.name.replace('/', '_')),
                ('res_model', '=', 'pos.session')]).unlink()

    def test_010_cancel_xml_session(self):
        """Call method that cancel XML, the XML is not cancelled by the time
        between the stamp and cancel."""
        self.create_order()
        self.session.create_xml_session()
        self.session.cancelate_xml_session()

    def test_012_create_credit_note_previous_open_invoice(self):
        """Create a credit note from a returned order with previous invoice
        validated in open state
        """
        order = self.create_order(self.partner2.id)
        # Creating Invoice
        order.action_pos_order_invoice()
        order.invoice_id.action_invoice_open()
        # Validating that the invoice state is open
        self.assertEqual(order.invoice_id.state, 'open',
                         'The invoice related to the order is not open')
        # Creating Refund
        refund = order.refund()
        # Validating if the refund was created
        self.assertTrue(refund.get('res_id'),
                        'The refund was not created')
        # Creating the object for the return
        refund = self.pos_order_obj.browse(refund.get('res_id'))
        # Creating payment
        payment = self.pmp_obj.with_context(active_id=order.id).create({
            'journal_id': order.session_id.config_id.journal_ids.ids[0],
            'amount': order.amount_total
        })
        payment.check()
        # Creating the credit note
        refund.action_pos_order_invoice()
        # Validate if the credit note was created and its state
        self.assertEqual((refund.invoice_id.state, refund.invoice_id.type),
                         ('paid', 'out_refund'),
                         'The credit note was not created')
        # Validating that the original invoice is paid too
        self.assertEqual(order.invoice_id.state, 'paid',
                         'The invoice related to the order is not paid')
        # Validating the state of the refund
        self.assertEqual(refund.state, 'invoiced',
                         'The state of the order was not updated')

    def test_013_create_credit_note_previous_paid_invoice(self):
        """Create a credit note from a returned order with previous invoice
        validated in paid state
        """
        order = self.create_order(self.partner2.id)
        # Creating Invoice
        order.action_pos_order_invoice()
        order.invoice_id.action_invoice_open()
        # Creating payment for the invoice
        pay_method = self.env['account.payment.method'].search(
            [('payment_type', '=', 'inbound')], limit=1)
        payment = self.payment.with_context(
            {'active_model': 'account.invoice',
             'active_id': order.invoice_id.id,
             'active_ids': order.invoice_id.ids}
        )
        values = payment.default_get([])
        values.update(journal_id=order.invoice_id.journal_id.id,
                      payment_method_id=pay_method.id)
        payment_id = payment.create(values)
        payment_id.create_payment()

        # Validating that the invoice state is paid
        self.assertEqual(order.invoice_id.state, 'paid',
                         'The invoice related to the order is not open')
        # Creating Refund
        refund = order.refund()
        # Validating if the refund was created
        self.assertTrue(refund.get('res_id'),
                        'The refund was not created')
        # Creating the object for the return
        refund = self.pos_order_obj.browse(refund.get('res_id'))
        # Creating payment
        payment = self.pmp_obj.with_context(active_id=order.id).create({
            'journal_id': order.session_id.config_id.journal_ids.ids[0],
            'amount': order.amount_total
        })
        payment.check()
        # Creating the credit note
        refund.action_pos_order_invoice()
        # Validate if the credit note was created and its state
        self.assertEqual((refund.invoice_id.state, refund.invoice_id.type),
                         ('paid', 'out_refund'),
                         'The credit note was not created')
        # Validating that the original invoice is paid too
        self.assertEqual(order.invoice_id.state, 'paid',
                         'The invoice related to the order is not paid')
        # Validating the state of the refund
        self.assertEqual(refund.state, 'invoiced',
                         'The state of the order was not updated')

    def test_014_create_credit_note(self):
        """Create a credit note from a returned order without previous invoice
        """
        order = self.create_order(self.partner2.id)

        # Creating Refund
        refund = order.refund()
        # Validating if the refund was created
        self.assertTrue(refund.get('res_id'),
                        'The refund was not created')
        # Creating the object for the return
        refund = self.pos_order_obj.browse(refund.get('res_id'))
        # Creating payment
        payment = self.pmp_obj.with_context(active_id=order.id).create({
            'journal_id': order.session_id.config_id.journal_ids.ids[0],
            'amount': order.amount_total
        })
        payment.check()
        # Creating the credit note
        refund.action_pos_order_invoice()
        # Validate if the credit note was created and its state
        self.assertEqual((refund.invoice_id.state, refund.invoice_id.type),
                         ('open', 'out_refund'),
                         'The credit note was not created')
        # Validating the state of the refund
        self.assertEqual(refund.state, 'invoiced',
                         'The state of the order was not updated')

    def create_order(self, partner=False):
        tax_ret = self.env.ref('l10n_mx.1_tax7')
        tax_ret.description = 'IVA'
        taxes = self.env.ref('l10n_mx.1_tax12').ids
        taxes.extend(tax_ret.ids)
        now = fields.Datetime.context_timestamp(
            self.pos_order_obj.with_context(tz='America/Mexico_City'),
            fields.Datetime.from_string(fields.Datetime.now()))
        order = self.pos_order_obj.with_env(self.env(user=self.uid)).create({
            'partner_id': partner or False,
            'session_id': self.session.id,
            'date_order': now,
            'lines': [(0, 0, {
                'product_id': self.product.id,
                'price_unit': 100.0,
                'qty': 1.0,
                'tax_ids': [(6, 0, [taxes])],
            })]
        })
        payment = self.pmp_obj.with_context(
            active_id=order.id).with_env(self.env(user=self.uid)).create({

                'journal_id': order.session_id.config_id.journal_ids.ids[0],
                'amount': order.amount_total
            })
        payment.check()
        order.action_create_invoice()
        order.action_validate_invoice()
        return order
