# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import base64
from datetime import datetime
from lxml import etree
from lxml.objectify import fromstring
from odoo import models, api, fields, _, tools
from odoo.tools.misc import formatLang
from odoo.tools.safe_eval import safe_eval
_logger = logging.getLogger(__name__)
try:
    from cfdilib import cfdv32
    from OpenSSL import crypto
except (ImportError, IOError) as err:
    _logger.debug(err)

XSLT_CADENA = 'l10n_mx_reports/data/xslt/BalanzaComprobacion_1_2.xslt'


class AccountReportContextCommon(models.TransientModel):
    _inherit = "account.report.context.common"

    def _report_name_to_report_model(self):
        res = super(
            AccountReportContextCommon, self)._report_name_to_report_model()
        name = '%s%s%sBN' % (
            self.env.user.company_id.vat or '',
            fields.date.today().year,
            str(fields.date.today().month).zfill(2))
        res[name] = 'l10n_mx.account.trial.balance.report'
        res['l10n_mx_trial_balance'] = 'l10n_mx.account.trial.balance.report'
        return res

    def _report_model_to_report_context(self):
        res = super(
            AccountReportContextCommon, self)._report_model_to_report_context()
        res['l10n_mx.account.trial.balance.report'] = (
            'l10n_mx.account.context.trial.balance')
        return res


class TrialBalanceContextMexico(models.Model):
    _inherit = "account.context.coa"
    _name = "l10n_mx.account.context.trial.balance"

    fold_field = 'unfolded_trial'
    unfolded_trial = fields.Many2many(
        'account.financial.html.report.line',
        'context_trial_to_financial_line',
        string='Unfolded lines', help='Save the unfolded lines.')

    def get_report_obj(self):
        return self.env['l10n_mx.account.trial.balance.report']

    def get_columns_names(self):
        columns = [_('Initial Balance')]
        if self.comparison and (
                self.periods_number == 1 or self.date_filter_cmp == 'custom'):
            columns += [_('Debit'), _('Credit')]
        elif self.comparison:
            for dummy_period in self.get_cmp_periods(display=True):
                columns += [_('Debit'), _('Credit')]
        # Completely overwritten to get proper header and Names for Columns.
        return columns + [_('Debit'), _('Credit'), _('End Balance')]


class AccountFinancialReportXMLExport(models.AbstractModel):
    _inherit = "account.financial.html.report.xml.export"

    @api.model
    def is_xml_export_balance_available(self, report_obj):
        if report_obj._name == 'l10n_mx.account.trial.balance.report':
            return True
        return False

    @api.model
    def is_xml_export_available(self, report_obj):
        if report_obj._name == 'l10n_mx.account.trial.balance.report':
            return True
        return super(AccountFinancialReportXMLExport,
                     self).is_xml_export_available(report_obj)

    def l10n_mx_edi_add_digital_stamp(self, cfdi, path_xslt):
        """Add digital stamp certificate attributes in XML report"""
        company = self.env.user.company_id
        if not company.certificate_id:
            return cfdi
        tree = fromstring(cfdi)
        xslt_root = etree.parse(tools.file_open(path_xslt))
        cadena = str(etree.XSLT(xslt_root)(tree))
        key_pem = base64.decodestring(company.certificate_id.file_key_pem)
        private_key = crypto.load_privatekey(crypto.FILETYPE_PEM, key_pem)
        cadena_crypted = crypto.sign(private_key, cadena, 'sha1')
        sello = base64.encodestring(cadena_crypted).replace('\n', '').replace(
            '\r', '')
        tree.attrib['Sello'] = sello
        return etree.tostring(tree, pretty_print=True, xml_declaration=True,
                              encoding='UTF-8')

    def get_trial_balance_dict(self, context_id):
        company = self.env.user.company_id
        xml_data = context_id.get_report_obj().with_context(
            no_format=True, print_mode=True).get_lines(context_id)
        accounts = []
        account_lines = [
            l for l in xml_data
            if l['type'] == 'account_id' and l.get('show', True)]
        account_obj = self.env['account.account']
        for line in account_lines:
            account = account_obj.browse(line['id'])
            tag = account.tag_ids.filtered(lambda r: r.color == 4)
            if not tag:
                continue
            cols = line.get('columns', [])
            initial, debit, credit, end = (
                float(cols[0] or 0), float(cols[1] or 0),
                float(cols[2] or 0), float(cols[3] or 0))
            accounts.append({
                'number': account.code,
                'initial': formatLang(
                    self.env, initial, digits=2, grouping=False),
                'debit': formatLang(
                    self.env, debit, digits=2, grouping=False),
                'credit': formatLang(
                    self.env, credit, digits=2, grouping=False),
                'end': formatLang(self.env, end, digits=2, grouping=False),
            })
        date = fields.datetime.strptime(context_id.date_from, "%Y-%m-%d")
        chart = {
            'vat': company.vat or '',
            'month': str(date.month).zfill(2),
            'year': date.year,
            'accounts': accounts,
            'type': 'N',
            'certificate_id': company.certificate_id or '',
        }
        return chart

    def do_xml_export(self, context_id):
        if context_id.get_report_obj()._name == (
                'l10n_mx.account.trial.balance.report'):
            balance = cfdv32.get_balance(self.get_trial_balance_dict(
                context_id))
            if bool(balance.ups):
                return balance.ups.message
            return self.l10n_mx_edi_add_digital_stamp(
                balance.document, XSLT_CADENA)
        return super(AccountFinancialReportXMLExport,
                     self).do_xml_export(context_id)

    def check(self, report_name, report_id=None):
        if report_name == 'l10n_mx.account.trial.balance.report':
            return True
        return super(AccountFinancialReportXMLExport, self).check(
            report_name, report_id=report_id)


class TrialBalanceMexico(models.AbstractModel):
    _inherit = "account.coa.report"
    _name = "l10n_mx.account.trial.balance.report"

    @api.model
    def get_lines(self, context_id, line_id=None):
        if isinstance(context_id, int):
            context_id = self.env[
                'l10n_mx.account.context.trial.balance'].search(
                    [['id', '=', context_id]])
        ctx = dict(self.env.context)
        ctx.update({
            'date_from': context_id.date_from,
            'date_to': context_id.date_to,
            'state': context_id.all_entries and 'all' or 'posted',
            'cash_basis': context_id.cash_basis,
            'hierarchy_3': context_id.hierarchy_3,
            'context_id': context_id,
            'company_ids': context_id.company_ids.ids,
            'periods_number': context_id.periods_number,
            'periods': [[context_id.date_from, context_id.date_to
                         ]] + context_id.get_cmp_periods(),
        })
        return self.with_context(ctx)._lines(line_id)

    @api.model
    def get_title(self):
        return _("Trial Balance")

    @api.model
    def get_name(self):
        # TODO Year and month must be taken from period selected in filters
        # Add in the code from report in SAT
        name = '%s%s%sBN' % (
            self.env.user.company_id.vat or '',
            fields.date.today().year,
            str(fields.date.today().month).zfill(2))
        return name

    @api.model
    def _lines(self, line_id=None):
        """ The lines need to be consistent to what CFDILib needs to build the
        XML.
        """
        afrl_obj = self.env['account.financial.html.report.line']
        context = self.env.context
        company_id = context.get('company_id') or self.env.user.company_id
        grouped_accounts = self.with_context(
            date_from_aml=context['date_from'],
            date_from=context['date_from'] and
            company_id.compute_fiscalyear_dates(
                datetime.strptime(context['date_from'], "%Y-%m-%d"))[
                    'date_from'] or None).group_by_account_id(None)  # noqa Aml go back to the beginning of the user chosen range but the amount on the account line should go back to either the beginning of the fy or the beginning of times depending on the account
        lines = []
        afr_lines = afrl_obj.search([
            ('parent_id', '=', False),
            ('code', 'ilike', 'MX_%')], order='code')
        if line_id:
            lines.extend(self._get_lines_second_level(
                afrl_obj.browse(line_id), grouped_accounts))
            return lines
        for line in afr_lines:
            childs = self._get_lines_second_level(
                line.children_ids, grouped_accounts)
            if not childs:
                continue
            lines.append({
                'id': line.id,
                'type': 'line',
                'name': line.name,
                'footnotes': {},
                'columns': ['', '', '', ''],
                'level': 1,
                'unfoldable': False,
                'unfolded': True,
            })
            lines.extend(childs)
        return lines

    @api.model
    def _get_lines_second_level(
            self, lines_child, grouped_accounts):
        """Return list of tags found in the second level"""
        lines = []
        sorted_childs = sorted(lines_child, key=lambda a: a.name)
        context = self.env.context
        unfold_all = context.get('print_mode')
        for child in sorted_childs:
            account_lines = self._get_lines_third_level(
                child, grouped_accounts)
            if not account_lines:
                continue
            lines.append({
                'id': child.id,
                'type': 'line',
                'name': child.name,
                'footnotes': {},
                'columns': ['', '', '', ''],
                'level': 2,
                'unfoldable': True,
                'unfolded': child in context['context_id'][
                    'unfolded_trial'] or unfold_all,
            })
            if child in context['context_id']['unfolded_trial'] or unfold_all:
                lines.extend(account_lines)
        return lines

    @api.model
    def _get_lines_third_level(self, line, grouped_accounts):
        """Return list of accounts found in the third level"""
        lines = []
        context = self.env.context
        account_ids = self.env['account.account'].search(
            safe_eval(line.domain or '[]'), order='code')
        for account in account_ids:
            account_group = grouped_accounts.get(account, {})
            if not account_group:
                continue
            name = account.code + " " + account.name
            name = name[:98] + "..." if len(
                name) > 100 and not context.get('print_mode') else name
            debit = account_group.get('debit') - account_group.get(
                'initial_bal', {}).get('debit', 0.0)
            credit = account_group.get('credit') - account_group.get(
                'initial_bal', {}).get('credit', 0.0)
            if not debit and not credit:
                continue
            lines.append({
                'id': account.id,
                'type': 'account_id',
                'name': name,
                'level': 3,
                'footnotes': {},
                'columns': [
                    self._format(account_group.get('initial_bal', {}).get(
                        'balance', 0.0)),
                    self._format(debit),
                    self._format(credit),
                    self._format(account_group.get('balance', 0.0))]
            })
        return lines
