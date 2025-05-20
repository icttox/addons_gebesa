# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from lxml import objectify
from dateutil.relativedelta import relativedelta
from .common import MexicoReportsTestCase


class AccountTrialBalance(MexicoReportsTestCase):

    def setUp(self):
        super(AccountTrialBalance, self).setUp()
        self.aml_obj = self.env['account.move.line']
        self.report_model = 'l10n_mx.account.trial.balance.report'
        self.afrl_obj = self.env['account.financial.html.report.line']
        self.account = self.account_obj.create({
            'name': 'Test Trial Balance',
            'code': '101.01.999',
            'user_type_id': self.account_type_cash.id,
            'tag_ids': [(4, self.env.ref('l10n_mx.account_tag_101_01').ids)],
        })

    def test_001_get_trial_balance_xml(self):
        """Verify that XML to trial balance report is generated"""
        context_data = self.report_common.return_context(self.report_model, {})
        data = self.env[context_data[0]].browse(context_data[1]).get_xml()
        self.assertTrue(data)

    def test_002_get_movement_in_other_period(self):
        """Verify that XML to trial balance report is generated,
        but not consider movements in other period"""
        self.create_move(self.date - relativedelta(months=1))
        context_data = self.report_common.return_context(self.report_model, {})
        data = self.env[context_data[0]].browse(context_data[1]).get_xml()
        xml = objectify.fromstring(data)
        accounts = [acc.get('NumCta') for acc in xml.Ctas]
        self.assertNotIn(self.account.code, accounts,
                         'Account without movements in this period.')

    def test_003_get_movement_account(self):
        """Verify that XML to trial balance report is generated,
        but not consider movements in other period"""
        self.create_move()
        context_data = self.report_common.return_context(self.report_model, {})
        data = self.env[context_data[0]].browse(context_data[1]).get_xml()
        xml = objectify.fromstring(data)
        account = [
            acc for acc in xml.Ctas if acc.get('NumCta') == self.account.code]
        self.assertTrue(account, 'Account with movements is not printed.')
        self.assertEquals(['100.00', '100.00', '101.01.999', '0.00', '0.00'],
                          [account[0].get(key) for key in account[0].keys()],
                          'Different values in XML')

    def test_004_get_trial_balance_unfold(self):
        """Verify that XML to Trial Balance report print all accounts"""
        self.create_move()
        context_data = self.report_common.return_context(self.report_model, {})
        data = self.env[context_data[0]].browse(context_data[1])
        data.unfolded_trial = self.env.ref('l10n_mx_reports.mx_afrl_101')
        base_domain = [
            ('date', '<=', data.date_to),
            ('date', '>=', data.date_from),
            ('move_id.state', '=', 'posted'),
            ('company_id', 'in', data.company_ids.ids)]
        data = data.get_xml()
        xml = objectify.fromstring(data)
        accounts = [acc.get('NumCta') for acc in xml.Ctas]
        count_acc = self.aml_obj.search(base_domain).mapped('account_id')
        self.assertEquals(
            len(accounts), len(count_acc), 'Not all accounts printed.')

    def create_move(self, date=False):
        self.move_obj.create({
            'name': 'Manually Trial Balance',
            'journal_id': self.journal.id,
            'date': date or self.date,
            'line_ids': [
                (0, 0, {
                    'name': 'Move1',
                    'journal_id': self.journal.id,
                    'account_id': self.account.id,
                    'debit': 100.0,
                }),
                (0, 0, {
                    'name': 'Move2',
                    'journal_id': self.journal.id,
                    'account_id': self.account.id,
                    'credit': 100.0,
                }),
            ]}).post()
