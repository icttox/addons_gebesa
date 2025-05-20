# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from lxml import objectify
from odoo.tools.safe_eval import safe_eval
from .common import MexicoReportsTestCase


class AccountCoA(MexicoReportsTestCase):

    def setUp(self):
        super(AccountCoA, self).setUp()
        self.report_model = 'l10n_mx.account.coa.report'
        self.afrl_obj = self.env['account.financial.html.report.line']
        self.tag1 = self.env.ref('l10n_mx.account_tag_101_01')

    def test_001_get_coa_xml(self):
        """Verify that XML to CoA report is generated"""
        self._prepare_accounts_coa()
        context_data = self.report_common.return_context(self.report_model, {})
        data = self.env[context_data[0]].browse(context_data[1]).get_xml()
        self.assertTrue(data)

    def test_002_get_coa_xml_misconfigured(self):
        """Verify that XML to CoA report is not generated with misconfigured
        accounts"""
        self.account_obj.create({
            'code': '989.09',
            'name': 'Account Test CoA',
            'user_type_id': self.account_type_cash.id,
        })
        context_data = self.report_common.return_context(self.report_model, {})
        data = self.financial_export.browse().check_data_coa_report(
            self.env[context_data[0]].browse(context_data[1]))
        self.assertIn(
            'This XML could not be generated because some accounts are not '
            'correctly configured', data)

    def test_003_get_coa_account_deprecated(self):
        """Verify that XML to CoA report not consider deprecated accounts"""
        self._prepare_accounts_coa()
        self.account_obj.create({
            'code': '101.01.999',
            'name': 'Account Test CoA',
            'deprecated': True,
            'user_type_id': self.account_type_cash.id,
            'tag_ids': [(4, self.tag1.ids)],
        })
        context_data = self.report_common.return_context(self.report_model, {})
        data = self.env[context_data[0]].browse(context_data[1]).get_xml()
        xml = objectify.fromstring(data)
        accounts = [acc.get('NumCta') for acc in xml.Ctas]
        self.assertNotIn('101.01.999', accounts, 'Deprecated account printed.')

    def test_004_get_coa_account_unfold(self):
        """Verify that XML to CoA report print all accounts"""
        self._prepare_accounts_coa()
        self.account_obj.create({
            'code': '101.01.999',
            'name': 'Account Test CoA',
            'user_type_id': self.account_type_cash.id,
            'tag_ids': [(4, self.tag1.ids)],
        })
        context_data = self.report_common.return_context(self.report_model, {})
        data = self.env[context_data[0]].browse(context_data[1])
        data.unfolded_financial = self.env.ref('l10n_mx_reports.mx_afrl_101')
        data = data.get_xml()
        xml = objectify.fromstring(data)
        accounts = [acc.get('NumCta') for acc in xml.Ctas]
        count_acc = self.account_obj.search_count(
            [('deprecated', '=', False)])
        self.assertEquals(
            len(accounts), count_acc, 'Not all accounts printed.')

    def _prepare_accounts_coa(self):
        """To allow generate the CoA report, prepare all accounts to set a tag
        that to account financial report lines created."""
        afr_lines = self.afrl_obj.search(
            [('parent_id', '=', False), ('code', 'ilike', 'MX_%')])
        accounts = []
        for domain in afr_lines.mapped('children_ids').mapped('domain'):
            account_ids = self.account_obj.search(safe_eval(domain or '[]'))
            accounts.extend(account_ids.ids)
        misconfigured = self.account_obj.search([('id', 'not in', accounts)])
        # The method hope only one record, by this reason is called with for
        for account in misconfigured:
            account.write({'tag_ids': [(4, [self.tag1.id])]})
