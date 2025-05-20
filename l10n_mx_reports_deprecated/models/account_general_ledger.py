# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from datetime import datetime
from odoo import models, api, fields, _
_logger = logging.getLogger(__name__)
try:
    from cfdilib import cfdv32
except ImportError as err:
    _logger.debug(err)

XSLT_CADENA = 'l10n_mx_reports/data/xslt/PolizasPeriodo_1_2.xslt'


class AccountReportContextCommon(models.TransientModel):
    _inherit = "account.report.context.common"  # noqa pylint: disable=consider-merging-classes-inherited

    def _report_name_to_report_model(self):
        res = super(
            AccountReportContextCommon, self)._report_name_to_report_model()
        name = '%s%s%sG' % (
            self.env.user.company_id.vat or '',
            fields.date.today().year,
            str(fields.date.today().month).zfill(2))
        res[name] = 'l10n_mx.account.general.ledger.report'
        res['l10n_mx_general_ledger'] = 'l10n_mx.account.general.ledger.report'
        return res

    def _report_model_to_report_context(self):
        res = super(
            AccountReportContextCommon, self)._report_model_to_report_context()
        res['l10n_mx.account.general.ledger.report'] = (
            'l10n_mx.account.context.general.ledger')
        return res


class GeneralLedgerContextMexico(models.Model):
    _inherit = "account.context.general.ledger"
    _name = "l10n_mx.account.context.general.ledger"

    fold_field = 'unfolded_moves'
    unfolded_moves = fields.Many2many(
        'account.move', 'context_to_account_move_gl_mx',
        string='Unfolded lines')
    journal_ids = fields.Many2many(
        'account.journal', relation='account_report_mx_gl_journals')
    available_journal_ids = fields.Many2many(
        'account.journal', relation='account_report_mx_gl_available_journal',
        default=lambda s: [(6, 0, s.env['account.journal'].search([]).ids)])

    def get_report_obj(self):
        return self.env['l10n_mx.account.general.ledger.report']

    def get_columns_names(self):
        return [_("Date"), _("Acc. Number"), _("Acc. Name"),
                _("Debit"), _("Credit")]

    @api.multi
    def get_columns_types(self):
        return ["date", "text", "text", "number", "number"]


class AccountFinancialReportXMLExport(models.AbstractModel):
    _inherit = "account.financial.html.report.xml.export"  # noqa pylint: disable=consider-merging-classes-inherited

    @api.model
    def is_xml_export_available(self, report_obj):
        if report_obj._name == 'l10n_mx.account.general.ledger.report':
            return True
        return super(AccountFinancialReportXMLExport,
                     self).is_xml_export_available(report_obj)

    def get_ledger_dict(self, context_id):
        company = self.env.user.company_id
        xml_data = context_id.get_report_obj().with_context(
            print_mode=True).get_lines(context_id)
        lines = [l['id'] for l in xml_data if l['level'] == 2]
        moves = self.env['account.move'].browse(lines)
        date = fields.datetime.strptime(context_id.date_from, "%Y-%m-%d")
        chart = {
            'vat': company.vat or '',
            'month': str(date.month).zfill(2),
            'year': date.year,
            'moves': moves,
            'type': 'AF',
            'certificate_id': company.certificate_id or '',
        }
        return chart

    def do_xml_export(self, context_id):
        if context_id.get_report_obj()._name == (
                'l10n_mx.account.general.ledger.report'):
            ledger = cfdv32.get_moves(self.get_ledger_dict(context_id))
            if bool(ledger.ups):
                return ledger.ups.message
            return self.l10n_mx_edi_add_digital_stamp(
                ledger.document, XSLT_CADENA)
        return super(AccountFinancialReportXMLExport,
                     self).do_xml_export(context_id)

    def check(self, report_name, report_id=None):
        if report_name == 'l10n_mx.account.general.ledger.report':
            return True
        return super(AccountFinancialReportXMLExport, self).check(
            report_name, report_id=report_id)


class JournalEntriesMexico(models.AbstractModel):
    _inherit = "account.general.ledger"
    _name = "l10n_mx.account.general.ledger.report"

    @api.model
    def get_name(self):
        # TODO Year and month must be taken from period selected in filters
        # Add in the code from report in SAT
        name = '%s%s%sG' % (
            self.env.user.company_id.vat or '',
            fields.date.today().year,
            str(fields.date.today().month).zfill(2))
        return name

    @api.model
    def get_lines(self, context_id, line_id=None):
        if isinstance(context_id, int):
            context_id = self.env[
                'l10n_mx.account.context.general.ledger'].search(
                    [['id', '=', context_id]])
        new_context = dict(self.env.context)
        new_context.update({
            'date_from': context_id.date_from,
            'date_to': context_id.date_to,
            'state': context_id.all_entries and 'all' or 'posted',
            'cash_basis': context_id.cash_basis,
            'context_id': context_id,
            'company_ids': context_id.company_ids.ids,
            'journal_ids': context_id.journal_ids.ids,
            'analytic_account_ids': context_id.analytic_account_ids,
            'analytic_tag_ids': context_id.analytic_tag_ids,
        })
        return self.with_context(new_context)._lines(line_id)

    @api.model
    def get_title(self):
        return _("General Ledger")

    def group_by_journal_id(self, line_id):
        journals = {}
        context = self.env.context
        move_obj = self.env['account.move.line']
        journal_ids = self.env['account.journal'].search([])
        for journal in journal_ids:
            journals[journal] = {}
            domain = [
                ('date', '<=', context['date_to']),
                ('company_id', 'in', context['company_ids']),
                ('journal_id', '=', journal.id)]
            if context['date_from_aml']:
                domain.append(('date', '>=', context['date_from_aml']))
            if context['state'] == 'posted':
                domain.append(('move_id.state', '=', 'posted'))
            if context.get('account_tag_ids'):
                domain += [('account_id.tag_ids', 'in', context[
                    'account_tag_ids'].ids)]
            if context.get('analytic_tag_ids'):
                domain += [
                    '|', ('analytic_account_id.tag_ids', 'in', context[
                        'analytic_tag_ids'].ids),
                    ('analytic_tag_ids', 'in', context[
                        'analytic_tag_ids'].ids)]
            if context.get('analytic_account_ids'):
                domain += [('analytic_account_id', 'in', context[
                    'analytic_account_ids'].ids)]
            if not context.get('print_mode'):
                #  fetch the 81 first amls. The report only displays the first
                # 80 amls. We will use the 81st to know if there are more than
                # 80 in which case a link to the list view must be displayed.
                journals[journal]['lines'] = move_obj.search(
                    domain, order='date', limit=81)
            else:
                journals[journal]['lines'] = move_obj.search(
                    domain, order='date')
        return journals

    @api.model
    def _lines(self, line_id=None):
        lines = []
        if line_id:
            lines.extend(self._get_lines_second_level(
                self.env['account.move'].browse(line_id)))
            return lines
        context = self.env.context
        company_id = context.get('company_id') or self.env.user.company_id
        grouped_journals = self.with_context(
            date_from_aml=context['date_from'],
            date_from=context['date_from'] and
            company_id.compute_fiscalyear_dates(datetime.strptime(
                context['date_from'], "%Y-%m-%d"))['date_from'] or
            None).group_by_journal_id(line_id)  # Aml go back to the beginning
        # of the user chosen range but the amount on the account line should
        # go back to either the beginning of the fy or the beginning of times
        # depending on the account
        sorted_journals = sorted(grouped_journals, key=lambda a: a.code)
        for journal in sorted_journals:
            if not grouped_journals[journal].get('lines', []):
                continue
            lines.append({
                'id': journal.id,
                'type': 'line',
                'name': journal.name,
                'footnotes': {},
                'columns': [],
                'level': 1,
                'unfoldable': False,
                'unfolded': True,
                'colspan': 6,
            })
            lines.extend(self._get_lines_second_level(
                grouped_journals[journal].get('lines', []).mapped('move_id')))
        return lines

    @api.model
    def _get_lines_second_level(self, move_ids):
        lines = []
        context = self.env.context
        unfold_all = context.get('print_mode') and not context[
            'context_id']['unfolded_moves']
        for move in move_ids:
            name = move.name
            name = name[:33] + "..." if len(name) > 35 else name
            context = self.env.context
            lines.append({
                'id': move.id,
                'type': 'line',
                'name': name,
                'footnotes': {},
                'columns': [move.date, '', '', '', ''],
                'level': 2,
                'unfoldable': True,
                'unfolded': move in context['context_id'][
                    'unfolded_moves'] or unfold_all,
            })
            if move in context['context_id'][
                    'unfolded_moves'] or unfold_all:
                lines.extend(self._get_lines_third_level(move))
        return lines

    @api.model
    def _get_lines_third_level(self, move):
        lines = []
        for line in move.line_ids:
            name = line.name
            name = name[:43] + "..." if len(name) > 45 else name
            lines.append({
                'id': line.id,
                'move_id': move.id,
                'action': line.get_model_id_and_name(),
                'type': 'move_line_id',
                'name': name,
                'footnotes': {},
                'columns': [
                    '', line.account_id.code, line.account_id.name,
                    line.debit, line.credit],
                'level': 3,
            })
        return lines
