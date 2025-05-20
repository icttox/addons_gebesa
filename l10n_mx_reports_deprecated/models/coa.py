# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from odoo import models, api, fields, _
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval
_logger = logging.getLogger(__name__)
try:
    from cfdilib import cfdv32
except (ImportError, IOError) as err:
    _logger.debug(err)

XSLT_CADENA = 'l10n_mx_reports/data/xslt/CatalogoCuentas_1_2.xslt'


class AccountReportContextCommon(models.TransientModel):
    _inherit = "account.report.context.common"  # noqa pylint: disable=consider-merging-classes-inherited

    def _report_name_to_report_model(self):
        res = super(
            AccountReportContextCommon, self)._report_name_to_report_model()
        name = '%s%s%sCT' % (
            self.env.user.company_id.vat or '',
            fields.date.today().year,
            str(fields.date.today().month).zfill(2))
        res[name] = 'l10n_mx.account.coa.report'
        res['l10n_mx_coa'] = 'l10n_mx.account.coa.report'
        return res

    def _report_model_to_report_context(self):
        res = super(
            AccountReportContextCommon, self)._report_model_to_report_context()
        res['l10n_mx.account.coa.report'] = 'l10n_mx.account.context.coa'
        return res


class COAContextMexico(models.Model):
    _inherit = "account.context.coa"
    _name = "l10n_mx.account.context.coa"

    fold_field = 'unfolded_financial'
    unfolded_financial = fields.Many2many(
        'account.financial.html.report.line', 'context_coa_to_financial_line',
        string='Unfolded lines', help='Save the unfolded lines.')

    def get_report_obj(self):
        return self.env['l10n_mx.account.coa.report']

    def get_columns_names(self):
        return [_("Nature")]

    @api.multi
    def get_columns_types(self):
        return ["text"]


class AccountFinancialReportXMLExport(models.AbstractModel):
    _inherit = "account.financial.html.report.xml.export"  # noqa pylint: disable = consider-merging-classes-inherited

    @api.model
    def is_xml_export_available(self, report_obj):
        if report_obj._name == 'l10n_mx.account.coa.report':
            return True
        return super(AccountFinancialReportXMLExport,
                     self).is_xml_export_available(report_obj)

    def get_coa_dict(self, context_id):
        xml_data = context_id.get_report_obj().with_context(
            print_mode=True).get_lines(context_id)
        accounts = []
        account_lines = [l for l in xml_data if l['type'] == 'account_id']
        account_obj = self.env['account.account']
        for line in account_lines:
            account = account_obj.browse(line['id'])
            tag = account.tag_ids.filtered(lambda r: r.color == 4)
            if not tag:
                continue
            accounts.append({
                'code': tag.name[:6],
                'number': account.code,
                'name': account.name,
                'level': '2',
                'nature': tag.nature,
            })
        chart = {
            'vat': self.env.user.company_id.vat or '',
            'month': str(fields.date.today().month).zfill(2),
            'year': fields.date.today().year,
            'accounts': accounts,
            'certificate_id': self.env.user.company_id.certificate_id or '',
        }
        return chart

    def do_xml_export(self, context_id):
        if context_id.get_report_obj()._name == 'l10n_mx.account.coa.report':
            data_check = self.check_data_coa_report(context_id)
            if data_check:
                raise ValidationError(data_check)
            coa = cfdv32.get_coa(self.get_coa_dict(context_id))
            if bool(coa.ups):
                return coa.ups.message
            return self.l10n_mx_edi_add_digital_stamp(
                coa.document, XSLT_CADENA)
        return super(AccountFinancialReportXMLExport,
                     self).do_xml_export(context_id)

    @api.model
    def check_data_coa_report(self, context):
        data = context.get_report_obj().get_lines(context)
        account_not_found = [l for l in data if l['id'] == 0]
        if account_not_found:
            return _('This XML could not be generated because some accounts '
                     'are not correctly configured and can not be added in '
                     'this report. This accounts are found in the section '
                     '"Misconfigured Accounts", please configure your tag and '
                     'try generate the report XML again.')
        return ''

    def check(self, report_name, report_id=None):
        if report_name == 'l10n_mx.account.coa.report':
            return True
        return super(AccountFinancialReportXMLExport, self).check(
            report_name, report_id=report_id)


class COAMexico(models.AbstractModel):
    _inherit = "account.coa.report"
    _name = "l10n_mx.account.coa.report"

    @api.model
    def get_name(self):
        # TODO Year and month must be taken from period selected in filters
        # Add in the code from report in SAT
        name = '%s%s%sCT' % (
            self.env.user.company_id.vat or '',
            fields.date.today().year,
            str(fields.date.today().month).zfill(2))
        return name

    @api.model
    def get_report_type(self):
        return self.env.ref('account_reports.account_report_type_nothing')

    @api.model
    def get_lines(self, context_id, line_id=None):
        if isinstance(context_id, int):
            context_id = self.env['l10n_mx.account.context.coa'].search(
                [['id', '=', context_id]])
        new_context = dict(self.env.context)
        new_context.update({
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
        return self.with_context(new_context)._lines(line_id)

    @api.model
    def get_title(self):
        return _("Electronic Accounting COA")

    @api.model
    def _lines(self, line_id=None):
        lines = []
        afrl_obj = self.env['account.financial.html.report.line']
        afr_lines = afrl_obj.search([
            ('parent_id', '=', False),
            ('code', 'ilike', 'MX_%')], order='code')
        if line_id:
            lines.extend(
                self._get_lines_second_level(afrl_obj.browse(line_id)))
            return lines
        for line in afr_lines:
            lines.append({
                'id': line.id,
                'type': 'line',
                'name': line.name,
                'footnotes': {},
                'columns': [''],
                'level': 1,
                'unfoldable': False,
                'unfolded': True,
            })
            lines.extend(self._get_lines_second_level(line.children_ids))
        lines.extend(self._get_accounts_not_found(afr_lines))
        return lines

    @api.model
    def _get_accounts_not_found(self, afr_lines):
        """Add the accounts that are not found with domains in the AFR
        lines, with this the is indicated the accounts that will not show in
        the report."""
        accounts = []
        lines = []
        account_obj = self.env['account.account']
        for domain in afr_lines.mapped('children_ids').mapped('domain'):
            account_ids = account_obj.search(
                safe_eval(domain or '[]'), order='code')
            accounts.extend(account_ids.ids)
        accounts = account_obj.search([
            ('id', 'not in', accounts),
            ('deprecated', '=', False)])
        if accounts:
            lines.append({
                'id': 0,
                'type': 'line',
                'name': _('Misconfigured Accounts'),
                'footnotes': {},
                'columns': [''],
                'level': 1,
            })
        for account in accounts:
            name = '%s %s' % (account.code, account.name)
            name = name[:133] + "..." if len(name) > 135 else name
            lines.append({
                'id': account.id,
                'type': 'account_id',
                'name': name,
                'footnotes': {},
                'columns': [''],
                'level': 3,
            })
        return lines

    @api.model
    def _get_lines_second_level(self, lines_child):
        """Return list of tags found in the second level"""
        lines = []
        sorted_childs = sorted(lines_child, key=lambda a: a.name)
        context = self.env.context
        unfold_all = context.get('print_mode')
        for child in sorted_childs:
            account_lines = self._get_lines_third_level(child)
            if not account_lines:
                continue
            lines.append({
                'id': child.id,
                'type': 'line',
                'name': child.name,
                'footnotes': {},
                'columns': [''],
                'level': 2,
                'unfoldable': True,
                'unfolded': child in context['context_id'][
                    'unfolded_financial'] or unfold_all,
            })
            if child in context['context_id'][
                    'unfolded_financial'] or unfold_all:
                lines.extend(account_lines)
        return lines

    @api.model
    def _get_lines_third_level(self, line):
        """Return list of accounts found in the third level"""
        lines = []
        domain = safe_eval(line.domain or '[]')
        domain.append((('deprecated', '=', False)))
        account_ids = self.env['account.account'].search(domain, order='code')
        for account in account_ids:
            name = '%s %s' % (account.code, account.name)
            name = name[:133] + "..." if len(name) > 135 else name
            tag = account.tag_ids.filtered(lambda r: r.color == 4)
            nature = dict(tag.fields_get()['nature']['selection']).get(
                tag.nature, '')
            lines.append({
                'name': name,
                'level': 3,
                'footnotes': {},
                'type': 'account_id',
                'id': account.id,
                'columns': [nature],
            })
        return lines
