# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.tools.misc import formatLang


class SaleGenericJsReport(models.AbstractModel):
    _name = "sale.generic.js.report"
    _description = "Chart of Sale Report"

    def _format(self, value, currency=False):
        if self.env.context.get('no_format'):
            return value
        currency_id = currency or self.env.user.company_id.currency_id
        if currency_id.is_zero(value):
            value = abs(value)
        res = formatLang(self.env, value, currency_obj=currency_id)
        return res

    def _do_query(self, line_id, group_by_partner=True, limit=False):
        context = dict(self._context or {})
        filter_date_order = context.get('filter_date_order')

        company_id = self.env.user.company_id.id
        if context.get('company_id'):
            company_id = context['company_id']
        if 'company_ids' in context:
            company_id = ','.join(map(str, context['company_ids']))
        params = [context['date_from'], context['date_to'], company_id]
        select = """
            SELECT so.partner_id,so.team_id,
                SUM(COALESCE(freight_amount * COALESCE(so.rate_mex, 1.00),0.00)),
                SUM(COALESCE(installation_amount * COALESCE(so.rate_mex, 1.00),0.00)),
                SUM(COALESCE(net_sale * COALESCE(so.rate_mex, 1.00),0.00))
            FROM sale_order AS so
            JOIN sale_order_line AS sol ON so.id = sol.order_id
            WHERE """

        if filter_date_order:
            select += """so.date_order AT TIME ZONE 'UTC' AT TIME ZONE 'America/Mexico_City' >= %s
                AND so.date_order AT TIME ZONE 'UTC' AT TIME ZONE 'America/Mexico_City' < CAST(CAST(%s AS DATE) +1  AS DATE)"""
        else:
            select += """so.date_validator AT TIME ZONE 'UTC' AT TIME ZONE 'America/Mexico_City' >= %s
                AND so.date_validator AT TIME ZONE 'UTC' AT TIME ZONE 'America/Mexico_City' < CAST(CAST(%s AS DATE) +1  AS DATE)"""

        select += """AND so.state NOT IN ('cancel','sent','draft')
                AND so.company_id IN (%s)
            GROUP BY so.partner_id,so.team_id
        """
        self.env.cr.execute(select, params)
        results = self.env.cr.fetchall()
        return results

    def do_query(self, line_id):
        results = self._do_query(line_id, group_by_partner=True, limit=False)
        new_result = {}
        for res in results:
            if res[1] not in new_result.keys():
                new_result[res[1]] = {}
            if res[0] not in new_result[res[1]].keys():
                new_result[res[1]][res[0]] = {
                    'freight_amount': res[2],
                    'installation_amount': res[3],
                    'net_sale': res[4],
                }
        return new_result

    def group_by_account_id(self, line_id):
        partners = {}
        results = self.do_query(line_id)
        for team_id, result_partner in results.items():
            team = self.env['crm.team'].browse(team_id)
            partners[team] = {}
            for partner_id, result in result_partner.items():
                partner = self.env['res.partner'].browse(partner_id)
                partners[team][partner] = result
        return partners

    @api.model
    def get_lines(self, context_id, line_id=None):
        if isinstance(context_id, int):
            context_id = self.env['sale.generic.js.report.context'].search([['id', '=', context_id]])
        new_context = dict(self.env.context)
        new_context.update({
            'date_from': context_id.date_from,
            'date_to': context_id.date_to,
            'filter_date_order': context_id.filter_date_order,
            'context_id': context_id,
            'company_ids': context_id.company_ids.ids,
            'periods_number': context_id.periods_number,
            'periods': [[context_id.date_from, context_id.date_to]] + context_id.get_cmp_periods(),
        })
        return self.with_context(new_context)._lines(line_id)

    @api.model
    def _lines(self, line_id=None):
        lines = []
        context = self.env.context
        company_id = context.get('company_id') or self.env.user.company_id
        grouped_partners = {}
        period_number = 0
        for period in context['periods']:
            res = self.with_context(
                date_from_aml=period[0], date_to=period[1],
                date_from=period[0] or None).group_by_account_id(line_id)
            # Aml go back to the beginning of the user chosen range but the
            # amount on the account line should go back to either the beginning
            # of the fy or the beginning of times depending on the account
            for team in res:
                if team not in grouped_partners.keys():
                    grouped_partners[team] = {}
                for partner in res[team]:
                    if partner not in grouped_partners[team].keys():
                        grouped_partners[team][partner] = [
                            {'freight_amount': 0,
                             'installation_amount': 0,
                             'net_sale': 0}
                            for p in context['periods']]
                    grouped_partners[team][partner][
                    	period_number] = res[team][partner]
            period_number += 1

        for team in sorted(grouped_partners.keys(),
                           key=lambda a: a.name):
            lines.append({
                'id': team.id,
                'type': 'line',
                'name': _("Team %s") % (team.name),
                'footnotes': [],
                'columns': sum([['', '', ''] for p in xrange(len(context[
                    'periods']))], []),
                'level': 1,
                'unfoldable': False,
                'unfolded': True,
            })
            for partner in sorted(grouped_partners[team].keys(),
                                  key=lambda a: a.name):
                lines.append({
                    'id': partner.id,
                    'type': 'partner_id',
                    'name': partner.name,
                    'footnotes': self.env.context['context_id']._get_footnotes(
                        'partner_id', partner.id),
                    'columns': sum(
                        [
                            [self._format(grouped_partners[team][partner][p]['freight_amount']) or '',
                             self._format(grouped_partners[team][partner][p]['installation_amount']) or '',
                             self._format(grouped_partners[team][partner][p]['net_sale']) or '']
                            for p in xrange(len(context['periods']))], []),
                    'level': 1,
                    'unfoldable': False,
                })
        return lines

    @api.model
    def get_title(self):
        return _("Chart of Sale")

    @api.model
    def get_name(self):
        return 'JS'

    @api.model
    def get_report_type(self):
        return 'date_range'

    def get_template(self):
        return 'report_sale_order_js.report_sale_js'


class SaleGenericJsReportContext(models.TransientModel):
    _name = "sale.generic.js.report.context"
    _description = "A particular context for the chart of account"
    #_inherit = "account.report.context.common"

    filter_date_order = fields.Boolean('Filter with order date', default=False)
    fold_field = 'unfolded_accounts'
    unfolded_accounts = fields.Many2many('res.partner', 'context_to_js_report', string='Unfolded lines')

    def get_report_obj(self):
        return self.env['sale.generic.js.report']

    def get_columns_names(self):
        temp = self.get_full_date_names(self.date_to, self.date_from)
        if not isinstance(temp, unicode):
            temp = temp.decode("utf-8")
        columns = [_('Flete') + '<br/>' + temp, _('Instalacion'), _('Venta Neta')]
        if self.comparison and (self.periods_number == 1 or self.date_filter_cmp == 'custom'):
            columns += [_('Flete') + '<br/>' + self.get_cmp_date(), _('Instalacion'), _('Venta Neta')]
        else:
            for period in self.get_cmp_periods(display=True):
                columns += [_('Flete') + '<br/>' + str(period), _('Instalacion'), _('Venta Neta')]
        return columns

    @api.multi
    def get_columns_types(self):
        types = ['number', 'number', 'number']
        if self.comparison and (self.periods_number == 1 or self.date_filter_cmp == 'custom'):
            types += ['number', 'number', 'number']
        else:
            for period in self.get_cmp_periods(display=True):
                types += ['number', 'number', 'number']
        return types

    @api.multi
    def get_html_and_data(self, given_context=None):
        res = super().get_html_and_data(
            given_context=given_context)
        res['report_context']['filter_date_order'] = self.read([
            'filter_date_order'])[0]['filter_date_order']
        return res


class AccountReportContextCommon(models.TransientModel):
    #_inherit = "account.report.context.common"

    def _report_model_to_report_context(self):
        res = super()._report_model_to_report_context()
        res['sale.generic.js.report'] = 'sale.generic.js.report.context'
        return res

    def _report_name_to_report_model(self):
        res = super()._report_name_to_report_model()
        res['generic_sale_js_report'] = 'sale.generic.js.report'
        return res
