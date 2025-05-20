# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from __future__ import division

from datetime import datetime

from odoo import _, api, fields, models
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, float_compare


class ReportPartnerLedger(models.AbstractModel):
    _name = "l10n_mx.account.diot"
    _description = "DIOT"

    @api.model
    def get_lines(self, context_id, line_id=None):
        if isinstance(context_id, int):
            context_id = self.env['l10n_mx.account.context.diot'].search(
                [['id', '=', context_id]])
        new_context = dict(self.env.context)
        account_types = []
        if 'receivable' in context_id.account_type:
            account_types.append('receivable')
        if 'payable' in context_id.account_type:
            account_types.append('payable')
        new_context.update({
            'date_from': context_id.date_from,
            'date_to': context_id.date_to,
            'state': context_id.all_entries and 'all' or 'posted',
            'cash_basis': context_id.cash_basis,
            'context_id': context_id,
            'company_ids': context_id.company_ids.ids,
            'account_types': account_types
        })
        return self.with_context(new_context)._lines(line_id)

    def do_query(self, line_id):
        select = ',\"account_move_line_account_tax_rel\".account_tax_id, SUM(\"account_move_line\".debit - \"account_move_line\".credit)'  # noqa
        sql = "SELECT \"account_move_line\".partner_id%s FROM %s WHERE %s%s AND \"account_move_line_account_tax_rel\".account_move_line_id = \"account_move_line\".id GROUP BY \"account_move_line\".partner_id, \"account_move_line_account_tax_rel\".account_tax_id"  # noqa
        context = self.env.context
        journal_ids = []
        for company in self.env['res.company'].browse(context[
                'company_ids']).filtered('tax_cash_basis_journal_id'):
            journal_ids.append(company.tax_cash_basis_journal_id.id)
        tax_ids = self.env['account.tax'].search([
            ('type_tax_use', '=', 'purchase'),
            ('use_cash_basis', '=', True)])
        account_tax_ids = tax_ids.mapped('cash_basis_account_id')
        move_ids = self.get_moves_diot()
        domain = [
            ('journal_id', 'in', journal_ids),
            ('account_id', 'not in', account_tax_ids.ids),
            ('tax_ids', '!=', False),
            ('id', 'in', move_ids),
        ]
        tables, where_clause, where_params = self.env[
            'account.move.line']._query_get(domain)
        tables += ',"account_move_line_account_tax_rel"'
        line_clause = (
            ' AND \"account_move_line\".partner_id = ' + str(line_id)
            if line_id else '')
        sql = sql % (select, tables, where_clause, line_clause)
        query = self.env.cr.mogrify(sql, where_params)
        self.env.cr.execute(query)
        results = self.env.cr.fetchall()
        result = {}
        for res in results:
            result.setdefault(res[0], {}).setdefault(res[1], res[2])
        return result

    def get_moves_diot(self):
        """Return all movements that are assigned to taxes that will be added
        in DIOT report. This movements have assigned the groups used in report
        """
        context = self.env.context
        company_obj = self.env['res.company']
        group_tax_ids = [self.env.ref('l10n_mx.tax_group_iva').id,
                         self.env.ref('l10n_mx.tax_group_iva_ret').id,
                         self.env.ref('l10n_mx.tax_group_iva_exent').id]
        tax_ids = self.env['account.tax'].search([
            ('type_tax_use', '=', 'purchase'),
            ('use_cash_basis', '=', True),
            ('tax_group_id', 'in', group_tax_ids)])
        account_tax_ids = tax_ids.mapped('cash_basis_account_id')
        journal_ids = [
            c.tax_cash_basis_journal_id.id for c in company_obj.browse(
                context['company_ids']).filtered('tax_cash_basis_journal_id')]
        base_domain = [
            ('date', '<=', context['date_to']),
            ('date', '>=', context['date_from_aml']),
            ('company_id', 'in', context['company_ids']),
            ('journal_id', 'in', journal_ids),
            ('account_id', 'not in', account_tax_ids.ids),
            ('tax_ids', '!=', False),
        ]
        if context['state'] == 'posted':
            base_domain.append(('move_id.state', '=', 'posted'))
        aml_ids = self.env['account.move.line'].search(base_domain)
        if not tax_ids or not aml_ids:
            # The taxes are not correctly configured
            return []
        query = 'SELECT account_move_line_id FROM account_move_line_account_tax_rel WHERE account_tax_id IN %s AND account_move_line_id in %s;' # noqa
        parameters = (tuple(tax_ids.ids), tuple(aml_ids.ids))
        moves_diot = self.env.cr.execute(query, parameters)
        moves_diot = self.env.cr.fetchall()
        return [m[0] for m in moves_diot]

    def group_by_partner_id(self, line_id):
        context = self.env.context
        partners = {}
        results = self.do_query(line_id)
        aml_obj = self.env['account.move.line']
        move_ids = self.with_context(context).get_moves_diot()
        for partner_id, result in results.items():
            domain = [
                ('partner_id', '=', partner_id),
                ('id', 'in', move_ids)]
            partner = self.env['res.partner'].browse(partner_id)
            partners[partner] = result
            if not context.get('print_mode'):
                #  fetch the 81 first amls. The report only displays the first
                # 80 amls. We will use the 81st to know if there are more than
                # 80 in which case a link to the list view must be displayed.
                lines = aml_obj.search(domain, order='date', limit=81)
            else:
                lines = aml_obj.search(domain, order='date')
            partners[partner]['lines'] = lines
        return partners

    @api.model
    def _lines(self, line_id=None):
        lines = []
        context = self.env.context
        company_id = context.get('company_id') or self.env.user.company_id
        grouped_partners = self.with_context(
            date_from_aml=context['date_from'], date_from=context[
                'date_from'] and company_id.compute_fiscalyear_dates(
                    datetime.strptime(
                        context['date_from'], DEFAULT_SERVER_DATE_FORMAT))[
                            'date_from'] or None).group_by_partner_id(line_id)
        # Aml go back to the beginning of the user chosen range but the
        # amount on the partner line should go back to either the beginning of
        # the fy or the beginning of times depending on the partner
        sorted_partners = sorted(grouped_partners, key=lambda p: p.name)
        unfold_all = context.get('print_mode') and not context['context_id'][
            'unfolded_partners']
        group_iva = self.env.ref('l10n_mx.tax_group_iva')
        group_ret = self.env.ref('l10n_mx.tax_group_iva_ret')
        group_exe = self.env.ref('l10n_mx.tax_group_iva_exent')
        tax_ids = self.env['account.tax'].search([
            ('type_tax_use', '=', 'purchase')])
        tax16 = tax_ids.filtered(
            lambda r: not float_compare(r.amount, 16.0, 0) and
            r.tax_group_id == group_iva)
        tax0 = tax_ids.filtered(lambda r: not float_compare(
            r.amount, 0.0, 0) and r.tax_group_id == group_iva)
        for partner in sorted_partners:
            if not partner:
                lines.extend(
                    self.get_lines_wo_partner(
                        grouped_partners[partner]['lines']))
                continue
            p_columns = [
                partner.l10n_mx_type_of_third or '',
                partner.l10n_mx_type_of_operation or '',
                partner.vat,
                partner.country_id.code or '',
                partner.l10n_mx_nationality or '']
            partner_data = grouped_partners[partner]
            total_tax16 = total_tax0 = exempt = withh = 0
            for tax in tax16.ids:
                total_tax16 += partner_data.get(tax, 0)
            p_columns.append(int(round(total_tax16, 0)))
            p_columns.append(0)
            total_tax0 += sum([partner_data.get(tax, 0) for tax in tax0.ids])
            p_columns.append(int(round(total_tax0, 0)))
            exempt += sum([partner_data.get(exem, 0)
                           for exem in tax_ids.filtered(
                               lambda r: r.tax_group_id == group_exe).ids])
            p_columns.append(int(round(exempt, 0)))
            withh += sum([abs(partner_data.get(ret.id, 0) / (100 / ret.amount))
                          for ret in tax_ids.filtered(
                              lambda r: r.tax_group_id == group_ret)])
            p_columns.append(int(round(withh, 0)))
            name = partner.name
            name = name[:38] + "..." if len(
                name) > 40 and not context.get('print_mode') else name
            lines.append({
                'id': partner.id,
                'type': 'line',
                'name': name,
                'footnotes': self.env.context['context_id']._get_footnotes(
                    'line', partner.id),
                'columns': p_columns,
                'level': 2,
                'unfoldable': True,
                'unfolded': partner in context['context_id'][
                    'unfolded_partners'] or unfold_all,
                'colspan': 1,
            })
            if not (partner in context['context_id']['unfolded_partners'] or
                    unfold_all):
                continue
            progress = 0
            domain_lines = []
            amls = grouped_partners[partner]['lines']
            too_many = False
            if len(amls) > 80 and not context.get('print_mode'):
                amls = amls[-80:]
                too_many = True
            for line in amls:
                if self.env.context['cash_basis']:
                    line_debit = line.debit_cash_basis
                    line_credit = line.credit_cash_basis
                else:
                    line_debit = line.debit
                    line_credit = line.credit
                if not line_credit and not line_debit:
                    continue
                progress = progress + line_debit - line_credit
                m_name = line.display_name
                m_name = m_name[:32] + "..." if m_name > 35 else m_name
                columns = ['', '', '', '']
                columns.append('')
                total_tax16 = 0
                total_tax0 = 0
                exempt = 0
                withh = 0
                total_tax16 += sum([
                    line.debit or line.credit * -1
                    for tax in tax16.ids if tax in line.tax_ids.ids])
                columns.append(int(round(total_tax16, 0)))
                columns.append(0)
                total_tax0 += sum([
                    line.debit or line.credit * -1
                    for tax in tax0.ids if tax in line.tax_ids.ids])
                columns.append(int(round(total_tax0, 0)))
                exempt += sum([line.debit or line.credit * -1
                               for exem in tax_ids.filtered(
                                   lambda r: r.tax_group_id == group_exe).ids
                               if exem in line.tax_ids.ids])
                columns.append(int(round(exempt, 0)))
                withh += sum([
                    abs((line.debit or line.credit * -1) / (100 / ret.amount))
                    for ret in tax_ids.filtered(
                        lambda r: r.tax_group_id == group_ret)
                    if ret.id in line.tax_ids.ids])
                columns.append(int(round(withh, 0)))
                domain_lines.append({
                    'id': line.id,
                    'type': 'move_line_id',
                    'move_id': line.move_id.id,
                    'action': line.get_model_id_and_name(),
                    'name': m_name,
                    'footnotes': self.env.context[
                        'context_id']._get_footnotes('move_line_id', line.id),
                    'columns': columns,
                    'level': 1,
                })
            domain_lines.append({
                'id': partner.id,
                'type': 'o_account_reports_domain_total',
                'name': _('Total') + ' ' + name,
                'footnotes': self.env.context['context_id']._get_footnotes(
                    'o_account_reports_domain_total', partner.id),
                'columns': p_columns,
                'level': 1,
            })
            if too_many:
                domain_lines.append({
                    'id': partner.id,
                    'type': 'too_many_partner',
                    'name': _('There are more than 80 items in this list, '
                              'click here to see all of them'),
                    'footnotes': [],
                    'colspan': 8,
                    'columns': [],
                    'level': 3,
                })
            lines += domain_lines
        return lines

    @api.model
    def get_lines_wo_partner(self, amls):
        lines = []
        context = self.env.context
        if not amls or not context.get('print_mode', False):
            return lines
        for line in amls:
            lines.append({
                'id': line.id,
                'type': 'line_wo_partner',
                'name': '',
                'footnotes': {},
                'columns': [],
                'level': 1,
            })
        return lines

    @api.model
    def get_title(self):
        return _('DIOT')

    @api.model
    def get_name(self):
        company = self.env.user.company_id
        vat = company.vat or ''
        return 'DIOT_%s_%s' % (vat, fields.date.today().strftime('%Y%m'))

    @api.model
    def get_report_type(self):
        return self.env.ref(
            'account_reports.account_report_type_date_range_no_comparison')

    @api.model
    def get_template(self):
        return 'account_reports.report_financial'


class ReportAccountDiotContext(models.TransientModel):
    _name = "l10n_mx.account.context.diot"
    _description = "A particular context for the DIOT report"
    _inherit = "account.report.context.common"

    fold_field = 'unfolded_partners'
    unfolded_partners = fields.Many2many(
        'res.partner', 'account_diot_to_partners', string='Unfolded lines')
    account_type = fields.Selection([
        ('receivable', 'Receivable Accounts'),
        ('payable', 'Payable Accounts'),
        ('receivable_payable', 'Receivable and Payable Accounts')],
        default='receivable_payable')

    def get_report_obj(self):
        return self.env['l10n_mx.account.diot']

    def get_columns_names(self):
        return [
            _('Operation'), _('Third'), _('VAT'), _('Country'),
            _('Nationality'), _('Paid 16%'), _('Importation 16%'),
            _('Paid 0%'), _('Exempt'), _('Withheld')]

    @api.multi
    def get_columns_types(self):
        return [
            "number", "number", "text", "text", "text", "number", "number",
            "number", "number", "number"]

    @api.multi
    def get_html_and_data(self, given_context=None):
        res = super(ReportAccountDiotContext, self).get_html_and_data(
            given_context=given_context)
        xml_export_obj = self.env['account.financial.html.report.xml.export']
        res['txt_export'] = xml_export_obj.is_txt_export_available(
            self.get_report_obj())
        return res


class AccountReportContextCommon(models.TransientModel):
    _inherit = "account.report.context.common"  # noqa pylint: disable=consider-merging-classes-inherited

    def _report_model_to_report_context(self):
        res = super(
            AccountReportContextCommon, self)._report_model_to_report_context()
        res.update({
            'l10n_mx.account.diot': 'l10n_mx.account.context.diot',
        })
        return res

    def _report_name_to_report_model(self):
        res = super(
            AccountReportContextCommon, self)._report_name_to_report_model()
        company = self.env.user.company_id
        vat = company.vat or ''
        name = 'DIOT_%s_%s' % (vat, fields.date.today().strftime('%Y%m'))
        res.update({
            name: 'l10n_mx.account.diot',
            'l10n_mx_account_diot': 'l10n_mx.account.diot',
        })
        return res


class AccountFinancialReportXMLExport(models.AbstractModel):
    _inherit = "account.financial.html.report.xml.export"  # noqa pylint: disable=consider-merging-classes-inherited

    @api.multi
    def is_txt_export_available(self, report_obj):
        if report_obj._name == 'l10n_mx.account.diot':
            return True
        return False

    @api.model
    def check(self, report_name, report_id=None):
        if report_name == 'l10n_mx.account.diot':
            return True
        return super(AccountFinancialReportXMLExport, self).check(
            report_name, report_id=report_id)

    def do_xml_export(self, context):
        if context.get_report_obj()._name == 'l10n_mx.account.diot':
            return self._l10n_mx_diot_txt_export(context)
        return super(
            AccountFinancialReportXMLExport, self).do_xml_export(context)

    @api.model
    def check_data_report(self, context):
        if isinstance(context, int):
            context = self.env['l10n_mx.account.context.diot'].browse(context)
        data = context.get_report_obj().with_context(
            print_mode=True).get_lines(context)
        lines_wo_partner = self.check_lines_wo_partner(
            [l for l in data if l.get('type', False) == 'line_wo_partner'])
        partner_wo_data = self.check_lines_partner_data(
            [l for l in data if l.get('type', False) == 'line'])
        return lines_wo_partner or partner_wo_data or False

    @api.multi
    def check_lines_wo_partner(self, lines):
        moves_wo_partner = []
        moves_wo_partner.extend([
            line['id'] for line in lines if line.get('id')])
        if not moves_wo_partner:
            return {}
        return {
            'type': 'ir.actions.act_window',
            'name': 'Moves without supplier',
            'res_model': 'account.move.line',
            'views': [[False, 'list'], [False, 'form']],
            'domain': [['id', 'in', moves_wo_partner]],
        }

    @api.multi
    def check_lines_partner_data(self, lines):
        partners = []
        partners.extend([line['id'] for line in lines if line.get('id')])
        partners = self.env['res.partner'].browse(
            partners)._get_not_partners_diot()
        if not partners:
            return {}
        return {
            'type': 'ir.actions.act_window',
            'name': _('Suppliers without information necessary for DIOT'),
            'res_model': 'res.partner',
            'views': [[False, 'list'], [False, 'form']],
            'domain': [
                ['id', 'in', partners.ids], ['active', 'in', [True, False]]],
        }

    def _l10n_mx_diot_txt_export(self, context):
        txt_data = context.get_report_obj().with_context(
            print_mode=True).get_lines(context)
        lines = ''
        for line in txt_data:
            if line.get('type', False) != 'line':
                continue
            columns = line.get('columns', [])
            if not any(columns[5:]):
                continue
            data = [''] * 23
            data[0] = columns[0]
            data[1] = columns[1]
            data[2] = columns[2] if columns[0] == '04' else ''
            data[3] = columns[2] if columns[0] != '04' else ''
            data[4] = u''.join(line.get('name', '')).encode(
                'utf-8').strip() if columns[0] == '05' else ''
            data[5] = columns[3] if columns[0] == '05' else ''
            data[6] = u''.join(columns[4]).encode(
                'utf-8').strip() if columns[0] == '05' else ''
            data[7] = int(columns[5]) if columns[5] else ''
            data[13] = int(columns[6]) if columns[6] else ''
            data[18] = int(columns[7]) if columns[7] else ''
            data[19] = int(columns[8]) if columns[8] else ''
            data[20] = int(columns[9]) if columns[9] else ''
            lines += '|'.join(map(str, data)) + '\n'
        return lines
