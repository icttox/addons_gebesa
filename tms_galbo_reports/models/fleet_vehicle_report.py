# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class ReportTmsFleetVehicle(models.AbstractModel):
    _name = "tms.fleet.vehicle"
    _description = "Trucks Report"
    _inherit = "tms.report"

    filter_date = {'date_from': '', 'date_to': '', 'filter': 'this_month'}
    filter_comparison = {'date_from': '', 'date_to': '', 'filter': 'no_comparison', 'number_period': 1}
    # filter_cash_basis = False
    filter_all_entries = False
    # filter_journals = True
    # filter_analytic = True
    filter_unfold_all = False

    def _get_templates(self):
        # import ipdb; ipdb.set_trace()
        templates = super()._get_templates()
        templates['tms_main_table_header_template'] = 'tms_galbo_reports.template_customer_table_header'
        # templates['tms_line_template'] = 'tms_galbo_reports.tms_line_template_general_ledger_report'
        return templates

    def _get_columns_name(self, options):
        columns = [
            {'name': ''},
            {'name': _("Unit")},
            {'name': _("Kms GPS"), 'class': 'number'},
            {'name': _("Travels"), 'class': 'number'},
            {'name': _("Rend. GPS"), 'class': 'number'},
            {'name': _("Cost/KM"), 'class': 'number'},
            {'name': _("Incom/KM"), 'class': 'number'},
            {'name': _("Margin"), 'class': 'number'},
            {'name': _("Faults"), 'class': 'number'}, ]
        if options.get('comparison') and options['comparison'].get('periods'):
            columns += [
                {'name': _("Kms GPS"), 'class': 'number'},
                {'name': _("Travels"), 'class': 'number'},
                {'name': _("Rend. GPS"), 'class': 'number'},
                {'name': _("Cost/KM"), 'class': 'number'},
                {'name': _("Incom/KM"), 'class': 'number'},
                {'name': _("Margin"), 'class': 'number'},
                {'name': _("Faults"), 'class': 'number'},
            ] * len(options['comparison']['periods'])
        return columns

    def _get_super_columns(self, options):
        date_cols = options.get('date') and [options['date']] or []
        date_cols += (options.get('comparison') or {}).get('periods', [])
        columns = reversed(date_cols)
        return {'columns': columns, 'x_offset': 1, 'merge': 2}

    def _get_with_statement(self, user_types, domain=None):
        # import ipdb; ipdb.set_trace()
        """ This function allow to define a WITH statement as prologue to the usual queries returned by query_get().
            It is useful if you need to shadow a table entirely and let the query_get work normally although you're
            fetching rows from your temporary table (built in the WITH statement) instead of the regular tables.

            @returns: the WITH statement to prepend to the sql query and the parameters used in that WITH statement
            @rtype: tuple(char, list)
        """
        sql = ''
        params = []

        #Cash basis option
        #-----------------
        #In cash basis, we need to show amount on income/expense accounts, but only when they're paid AND under the payment date in the reporting, so
        #we have to make a complex query to join aml from the invoice (for the account), aml from the payments (for the date) and partial reconciliation
        #(for the reconciled amount).
        # if self.env.context.get('cash_basis'):
        #     if not user_types:
        #         return sql, params
        #     #we use query_get() to filter out unrelevant journal items to have a shadowed table as small as possible
        #     tables, where_clause, where_params = self.env['account.move.line']._query_get(domain=domain)
        #     sql = """WITH account_move_line AS (
        #       SELECT \"account_move_line\".id, \"account_move_line\".date, \"account_move_line\".name, \"account_move_line\".debit_cash_basis, \"account_move_line\".credit_cash_basis, \"account_move_line\".move_id, \"account_move_line\".account_id, \"account_move_line\".journal_id, \"account_move_line\".balance_cash_basis, \"account_move_line\".amount_residual, \"account_move_line\".partner_id, \"account_move_line\".reconciled, \"account_move_line\".company_id, \"account_move_line\".company_currency_id, \"account_move_line\".amount_currency, \"account_move_line\".balance, \"account_move_line\".user_type_id, \"account_move_line\".analytic_account_id
        #        FROM """ + tables + """
        #        WHERE (\"account_move_line\".journal_id IN (SELECT id FROM account_journal WHERE type in ('cash', 'bank'))
        #          OR \"account_move_line\".move_id NOT IN (SELECT DISTINCT move_id FROM account_move_line WHERE user_type_id IN %s))
        #          AND """ + where_clause + """
        #       UNION ALL
        #       (
        #        WITH payment_table AS (
        #          SELECT aml.move_id, \"account_move_line\".date,
        #                 CASE WHEN (aml.balance = 0 OR sub_aml.total_per_account = 0)
        #                     THEN 0
        #                     ELSE part.amount / ABS(sub_aml.total_per_account)
        #                 END as matched_percentage
        #            FROM account_partial_reconcile part
        #            LEFT JOIN account_move_line aml ON aml.id = part.debit_move_id
        #            LEFT JOIN (SELECT move_id, account_id, ABS(SUM(balance)) AS total_per_account
        #                         FROM account_move_line
        #                         GROUP BY move_id, account_id) sub_aml
        #                     ON (aml.account_id = sub_aml.account_id AND sub_aml.move_id=aml.move_id)
        #            LEFT JOIN account_move am ON aml.move_id = am.id,""" + tables + """
        #            WHERE part.credit_move_id = "account_move_line".id
        #             AND "account_move_line".user_type_id IN %s
        #             AND """ + where_clause + """
        #          UNION ALL
        #          SELECT aml.move_id, \"account_move_line\".date,
        #                 CASE WHEN (aml.balance = 0 OR sub_aml.total_per_account = 0)
        #                     THEN 0
        #                     ELSE part.amount / ABS(sub_aml.total_per_account)
        #                 END as matched_percentage
        #            FROM account_partial_reconcile part
        #            LEFT JOIN account_move_line aml ON aml.id = part.credit_move_id
        #            LEFT JOIN (SELECT move_id, account_id, ABS(SUM(balance)) AS total_per_account
        #                         FROM account_move_line
        #                         GROUP BY move_id, account_id) sub_aml
        #                     ON (aml.account_id = sub_aml.account_id AND sub_aml.move_id=aml.move_id)
        #            LEFT JOIN account_move am ON aml.move_id = am.id,""" + tables + """
        #            WHERE part.debit_move_id = "account_move_line".id
        #             AND "account_move_line".user_type_id IN %s
        #             AND """ + where_clause + """
        #        )
        #        SELECT aml.id, ref.date, aml.name,
        #          CASE WHEN aml.debit > 0 THEN ref.matched_percentage * aml.debit ELSE 0 END AS debit_cash_basis,
        #          CASE WHEN aml.credit > 0 THEN ref.matched_percentage * aml.credit ELSE 0 END AS credit_cash_basis,
        #          aml.move_id, aml.account_id, aml.journal_id,
        #          ref.matched_percentage * aml.balance AS balance_cash_basis,
        #          aml.amount_residual, aml.partner_id, aml.reconciled, aml.company_id, aml.company_currency_id, aml.amount_currency, aml.balance, aml.user_type_id, aml.analytic_account_id
        #         FROM account_move_line aml
        #         RIGHT JOIN payment_table ref ON aml.move_id = ref.move_id
        #         WHERE journal_id NOT IN (SELECT id FROM account_journal WHERE type in ('cash', 'bank'))
        #           AND aml.move_id IN (SELECT DISTINCT move_id FROM account_move_line WHERE user_type_id IN %s)
        #       )
        #     ) """
        #     params = [tuple(user_types.ids)] + where_params + [tuple(user_types.ids)] + where_params + [tuple(user_types.ids)] + where_params + [tuple(user_types.ids)]
        return sql, params

    # def _do_query_unaffected_earnings(self, options, line_id, company=None):
    #     ''' Compute the sum of ending balances for all accounts that are of a type that does not bring forward the balance in new fiscal years.
    #         This is needed to balance the trial balance and the general ledger reports (to have total credit = total debit)
    #     '''

    #     select = '''
    #     SELECT COALESCE(SUM("account_move_line".balance), 0),
    #            COALESCE(SUM("account_move_line".amount_currency), 0),
    #            COALESCE(SUM("account_move_line".debit), 0),
    #            COALESCE(SUM("account_move_line".credit), 0)'''
    #     if options.get('cash_basis'):
    #         select = select.replace('debit', 'debit_cash_basis').replace('credit', 'credit_cash_basis').replace('balance', 'balance_cash_basis')
    #     select += " FROM %s WHERE %s"
    #     user_types = self.env['account.account.type'].search([('type', 'in', ('receivable', 'payable'))])
    #     with_sql, with_params = self._get_with_statement(user_types)
    #     aml_domain = [('user_type_id.include_initial_balance', '=', False)]
    #     if company:
    #         aml_domain += [('company_id', '=', company.id)]
    #     tables, where_clause, where_params = self.env['account.move.line']._query_get(domain=aml_domain)
    #     query = select % (tables, where_clause)
    #     self.env.cr.execute(with_sql + query, with_params + where_params)
    #     res = self.env.cr.fetchone()
    #     date = self._context.get('date_to') or fields.Date.today()
    #     currency_convert = lambda x: company and company.currency_id._convert(x, self.env.user.company_id.currency_id, self.env.user.company_id, date) or x
    #     return {'balance': currency_convert(res[0]), 'amount_currency': res[1], 'debit': currency_convert(res[2]), 'credit': currency_convert(res[3])}

    def _do_query(self, options, line_id, group_by_vehicle=True, limit=False):
        company = self.env['res.company'].browse(self._context.get('company_id')) or self.env['res.users']._get_company()
        params = [
            self._context.get('date_from_aml'), self._context.get('date_to'),
            self._context.get('date_from_aml'), self._context.get('date_to'),
            company.id]
        if group_by_vehicle:
            query = """
                SELECT
                    fv.id "id",
                    fv.idname "unidad",
                    SUM(ROUND(CAST(te.distance_real AS decimal), 2)) "kms_gps",
                    COUNT(tt.id) "viajes",
                    ROUND(CAST(SUM(te.distance_real) / SUM(CASE WHEN te.fuel_qty = 0 THEN 1 ELSE te.fuel_qty END) AS decimal), 2) "rend_gps",
                    ROUND(CAST(SUM(te.amount_total_total) / SUM(te.distance_real) AS decimal), 2) "costo_km",
                    ROUND(CAST(SUM(tt.amount_untaxed) / SUM(te.distance_real) AS decimal), 2) "ingreso_km",
                    ROUND(CAST(((SUM(tt.amount_untaxed) - SUM(te.amount_total_total)) / SUM(CASE WHEN tt.amount_untaxed = 0 THEN 1 ELSE tt.amount_untaxed END)) * 100 AS decimal) , 2) "margen",
                    COUNT(tme.id) "averias"
            """
        else:
            query = """
                SELECT fv.id "id",
                    fv.idname "unidad",
                    ROUND(CAST(te.distance_real AS decimal), 2) "kms_gps",
                    tt.id "viajes",
                    ROUND(CAST(te.distance_real / CASE WHEN te.fuel_qty = 0 THEN 1 ELSE te.fuel_qty END AS decimal), 2) "rend_gps",
                    ROUND(CAST(te.amount_total_total / te.distance_real AS decimal), 2) "costo_km",
                    ROUND(CAST(tt.amount_untaxed / te.distance_real AS decimal), 2) "ingreso_km",
                    ROUND(CAST(((tt.amount_untaxed - te.amount_total_total) / CASE WHEN tt.amount_untaxed = 0 THEN 1 ELSE tt.amount_untaxed END) * 100 AS decimal) , 2) "margen",
                    tme.id "averias"
            """
        query += """
            FROM tms_travel tt
            JOIN tms_expense te ON te.id = tt.expense_id
            JOIN hr_employee he ON he.id = tt.employee_id
            JOIN fleet_vehicle fv ON fv.id = tt.unit_id
            JOIN operating_unit AS ou ON tt.operating_unit_id = ou.id
            LEFT JOIN tms_event tme ON tme.travel_id = tt.id
                    AND NOT tme.positive
                    AND tme.type = 'workshop'
                    AND tme.date >= %s
                    AND tme.date <= %s
            WHERE tt.date >= %s
                AND tt.date <= %s
                AND ou.company_id = %s
                AND tt.expense_id IS NOT null
        """
        if line_id:
            query += """ AND fv.id = %s"""
            params.append(line_id)
        if group_by_vehicle:
            query += """
                GROUP BY fv.id
            """
        query += """order by fv.name"""

        # if group_by_vehicle:
        #     select = "SELECT \"account_move_line\".account_id"
        #     select += ',COALESCE(SUM(\"account_move_line\".debit-\"account_move_line\".credit), 0),SUM(\"account_move_line\".amount_currency),SUM(\"account_move_line\".debit),SUM(\"account_move_line\".credit)'
        #     # if options.get('cash_basis'):
        #     #     select = select.replace('debit', 'debit_cash_basis').replace('credit', 'credit_cash_basis').replace('balance', 'balance_cash_basis')
        # else:
        #     select = "SELECT \"account_move_line\".id"
        # sql = "%s FROM %s WHERE %s%s"
        # if group_by_vehicle:
        #     sql +=  "GROUP BY \"account_move_line\".account_id"
        # else:
        #     sql += " GROUP BY \"account_move_line\".id"
        #     sql += " ORDER BY MAX(\"account_move_line\".date),\"account_move_line\".id"
        #     if limit and isinstance(limit, int):
        #         sql += " LIMIT " + str(limit)
        # user_types = self.env['account.account.type'].search([('type', 'in', ('receivable', 'payable'))])
        # with_sql, with_params = self._get_with_statement(user_types)
        # tables, where_clause, where_params = self.env['account.move.line']._query_get()
        # line_clause = line_id and ' AND \"account_move_line\".account_id = ' + str(line_id) or ''
        # query = sql % (select, tables, where_clause, line_clause)
        # self.env.cr.execute(with_sql + query, with_params + where_params)
        self.env.cr.execute(query, tuple(params))
        results = self.env.cr.fetchall()
        return results

    def _do_query_group_by_vehicle(self, options, line_id):
        # import ipdb; ipdb.set_trace()
        results = self._do_query(options, line_id, group_by_vehicle=True, limit=False)
        used_currency = self.env.user.company_id.currency_id
        company = self.env['res.company'].browse(self._context.get('company_id')) or self.env['res.users']._get_company()
        date = self._context.get('date_to') or fields.Date.today()
        def build_converter(currency):
            def convert(amount):
                return currency._convert(amount, used_currency, company, date)
            return convert

        compute_table = {
            a.id: build_converter(a.company_id.currency_id)
            for a in self.env['fleet.vehicle'].browse([k[0] for k in results])
        }
        results = dict([(
            k[0], {
                'km_gps': compute_table[k[0]](k[2]) if k[0] in compute_table else k[2],
                'viajes': k[3],
                'rend_gps': compute_table[k[0]](k[4]) if k[0] in compute_table else k[4],
                'costo_km': compute_table[k[0]](k[5]) if k[0] in compute_table else k[5],
                'ingreso_km': compute_table[k[0]](k[6]) if k[0] in compute_table else k[6],
                'margen': compute_table[k[0]](k[7]) if k[0] in compute_table else k[7],
                'averias': k[8],
            }
        ) for k in results])
        return results

    def _group_by_vehicle_id(self, options, line_id):
        # import ipdb; ipdb.set_trace()
        vehicles = {}
        results = self._do_query_group_by_vehicle(options, line_id)
        # initial_bal_date_to = fields.Date.from_string(self.env.context['date_from_aml']) + timedelta(days=-1)
        # initial_bal_results = self.with_context(date_to=initial_bal_date_to.strftime('%Y-%m-%d'))._do_query_group_by_vehicle(options, line_id)

        context = self.env.context

        # last_day_previous_fy = self.env.user.company_id.compute_fiscalyear_dates(fields.Date.from_string(self.env.context['date_from_aml']))['date_from'] + timedelta(days=-1)
        # unaffected_earnings_per_company = {}
        # for cid in context.get('company_ids', []):
        #     company = self.env['res.company'].browse(cid)
        #     # unaffected_earnings_per_company[company] = self.with_context(date_to=last_day_previous_fy.strftime('%Y-%m-%d'), date_from=False)._do_query_unaffected_earnings(options, line_id, company)

        # unaff_earnings_treated_companies = set()
        # unaffected_earnings_type = self.env.ref('account.data_unaffected_earnings')
        for vehicle_id, result in results.items():
            vehicle = self.env['fleet.vehicle'].browse(vehicle_id)
            vehicles[vehicle] = result
            # vehicles[vehicle]['initial_bal'] = initial_bal_results.get(vehicle.id, {'balance': 0, 'amount_currency': 0, 'debit': 0, 'credit': 0})

            ### if account.user_type_id == unaffected_earnings_type and account.company_id not in unaff_earnings_treated_companies:
            ###     #add the benefit/loss of previous fiscal year to unaffected earnings accounts
            ###     unaffected_earnings_results = unaffected_earnings_per_company[account.company_id]
            ###     for field in ['balance', 'debit', 'credit']:
            ###         accounts[account]['initial_bal'][field] += unaffected_earnings_results[field]
            ###         accounts[account][field] += unaffected_earnings_results[field]
            ###     unaff_earnings_treated_companies.add(account.company_id)
            #use query_get + with statement instead of a search in order to work in cash basis too
            # aml_ctx = {}
            # if context.get('date_from_aml'):
            #     aml_ctx = {
            #         'strict_range': True,
            #         'date_from': context['date_from_aml'],
            #     }
            travel_ids = self._do_query(options, vehicle.id, group_by_vehicle=False)
            # travel_ids = [x[3] for x in travel_ids]
            vehicles[vehicle]['total_lines'] = len(travel_ids)
            offset = int(options.get('lines_offset', 0))
            if self.MAX_LINES:
                stop = offset + self.MAX_LINES
            else:
                stop = None
            if not context.get('print_mode'):
                travel_ids = travel_ids[offset:stop]

            # vehicles[vehicle]['lines'] = self.env['tms.travel'].browse(travel_ids)
            vehicles[vehicle]['lines'] = travel_ids

        # For each company, if the unaffected earnings account wasn't in the selection yet: add it manually
        ### user_currency = self.env.user.company_id.currency_id
        ### for cid in context.get('company_ids', []):
        ###     company = self.env['res.company'].browse(cid)
        ###     if company not in unaff_earnings_treated_companies and not float_is_zero(unaffected_earnings_per_company[company]['balance'], precision_digits=user_currency.decimal_places):
        ###         unaffected_earnings_account = self.env['account.account'].search([
        ###             ('user_type_id', '=', unaffected_earnings_type.id), ('company_id', '=', company.id)
        ###         ], limit=1)
        ###         if unaffected_earnings_account and (not line_id or unaffected_earnings_account.id == line_id):
        ###             accounts[unaffected_earnings_account[0]] = unaffected_earnings_per_company[company]
        ###             accounts[unaffected_earnings_account[0]]['initial_bal'] = unaffected_earnings_per_company[company]
        ###             accounts[unaffected_earnings_account[0]]['lines'] = []
        ###             accounts[unaffected_earnings_account[0]]['total_lines'] = 0
        return vehicles

    # def _get_taxes(self, journal):
    #     tables, where_clause, where_params = self.env['account.move.line']._query_get()
    #     query = """
    #         SELECT rel.account_tax_id, SUM("account_move_line".balance) AS base_amount
    #         FROM account_move_line_account_tax_rel rel, """ + tables + """
    #         WHERE "account_move_line".id = rel.account_move_line_id
    #             AND """ + where_clause + """
    #        GROUP BY rel.account_tax_id"""
    #     self.env.cr.execute(query, where_params)
    #     ids = []
    #     base_amounts = {}
    #     for row in self.env.cr.fetchall():
    #         ids.append(row[0])
    #         base_amounts[row[0]] = row[1]

    #     res = {}
    #     for tax in self.env['account.tax'].browse(ids):
    #         self.env.cr.execute('SELECT sum(debit - credit) FROM ' + tables + ' '
    #             ' WHERE ' + where_clause + ' AND tax_line_id = %s', where_params + [tax.id])
    #         res[tax] = {
    #             'base_amount': base_amounts[tax.id],
    #             'tax_amount': self.env.cr.fetchone()[0] or 0.0,
    #         }
    #         if journal.get('type') == 'sale':
    #             #sales operation are credits
    #             res[tax]['base_amount'] = res[tax]['base_amount'] * -1
    #             res[tax]['tax_amount'] = res[tax]['tax_amount'] * -1
    #     return res

    def _post_process(self, grouped_vehicle, options, comparison_table, line_id):
        lines = []
        context = self.env.context
        company_id = context.get('company_id') or self.env.user.company_id

        sorted_vehicle = sorted(grouped_vehicle, key=lambda a: a.idname)
        unfold_all = context.get('print_mode') and len(options.get('unfolded_lines')) == 0
        col_total = {}
        for vehicle in sorted_vehicle:
            display_name = vehicle.idname
            cols = []
            travels_lines = []
            for period in range(len(comparison_table)):
                km_gps = grouped_vehicle[vehicle][period]['km_gps']
                viajes = grouped_vehicle[vehicle][period]['viajes']
                costo_km = grouped_vehicle[vehicle][period]['costo_km']
                ingreso_km = grouped_vehicle[vehicle][period]['ingreso_km']
                rend_gps = grouped_vehicle[vehicle][period]['rend_gps']
                margen = grouped_vehicle[vehicle][period]['margen']
                averias = grouped_vehicle[vehicle][period]['averias']

                if period not in col_total:
                    col_total[period] = {
                        'km_gps': 0, 'viajes': 0, 'costo_km': 0,
                        'ingreso_km': 0, 'rend_gps': 0, 'margen': 0,
                        'averias': 0}

                col_total[period]['km_gps'] += km_gps
                col_total[period]['viajes'] += viajes
                col_total[period]['averias'] += averias

                cols += [
                    {'name': km_gps}, {'name': viajes}, {'name': rend_gps},
                    {'name': costo_km}, {'name': ingreso_km}, {'name': margen},
                    {'name': averias},
                ]

                if 'vehicle_%s' % (vehicle.id,) in options.get('unfolded_lines') or unfold_all:
                    for travel in grouped_vehicle[vehicle][period]['lines']:
                        travel_id = self.env['tms.travel'].browse([travel[3]])
                        event_id = self.env['tms.event'].browse([travel[8]])
                        name = travel_id.name and travel_id.name or ''
                        name_title = name
                        # Don't split the name when printing
                        if len(name) > 35 and not self.env.context.get('no_format') and not self.env.context.get('print_mode'):
                            name = name[:32] + "..."
                        caret_type = 'tms.travel'
                        action_context = {
                        }
                        columns = [{'name': display_name}]
                        columns += [{'name': ''} for v in range(7 * period)]
                        columns += [{'name': v} for v in [
                            travel[2], travel_id.name, travel[4], travel[5],
                            travel[6], travel[7], event_id.name]]
                        columns[0]['class'] = 'whitespace_print'
                        columns[0]['title'] = name_title
                        line_value = {
                            'id': travel_id.id,
                            'action_context': action_context,
                            'caret_options': caret_type,
                            'class': 'top-vertical-align',
                            'parent_id': 'vehicle_%s' % (vehicle.id,),
                            'name': travel_id.name if travel_id.name else '/',
                            'columns': columns,
                            'level': 4,
                        }
                        travels_lines.append(line_value)

            lines.append({
                'id': 'vehicle_%s' % (vehicle.id,),
                'name': len(display_name) > 40 and not context.get('print_mode') and display_name[:40]+'...' or display_name,
                'title_hover': display_name,
                'columns': cols,
                'level': 2,
                'unfoldable': True,
                'unfolded': 'vehicle_%s' % (vehicle.id,) in options.get('unfolded_lines') or unfold_all,
                'colspan': 2,
            })

            if 'vehicle_%s' % (vehicle.id,) in options.get('unfolded_lines') or unfold_all:
                lines += travels_lines

        if not line_id:
            col = [{'name': ''}]
            for period in col_total:
                # for key in col_total[period]:
                col.append({'name': col_total[period]['km_gps']})
                col.append({'name': col_total[period]['viajes']})
                col.append({'name': ''})
                col.append({'name': ''})
                col.append({'name': ''})
                col.append({'name': ''})
                col.append({'name': col_total[period]['averias']})

            lines.append({
                'id': 'general_ledger_total_%s' % company_id.id,
                'name': _('Total'),
                'class': 'total',
                'level': 1,
                'columns': col,
            })
        return lines

    def _get_lines(self, options, line_id=None):
        lines = []
        grouped_vehicle = {}
        line_id = line_id and int(line_id.split('_')[1]) or None
        company_id = self.env.user.company_id
        comparison_table = [options.get('date')]
        comparison_table += options.get('comparison') and options[
            'comparison'].get('periods') or []

        # get the balance of accounts for each period
        period_number = 0
        for period in reversed(comparison_table):
            res = self.with_context(
                date_from_aml=period['date_from'],
                date_to=period['date_to'],
                date_from=period['date_from'] and company_id.compute_fiscalyear_dates(
                    fields.Date.from_string(period['date_from']))['date_from'] or None
            )._group_by_vehicle_id(options, line_id)

            for vehicle in res:
                if vehicle not in grouped_vehicle:
                    grouped_vehicle[vehicle] = [
                        {
                            'km_gps': 0, 'viajes': 0, 'costo_km': 0,
                            'ingreso_km': 0, 'rend_gps': 0, 'margen': 0,
                            'averias': 0, 'lines': []} for p in comparison_table]
                grouped_vehicle[vehicle][period_number]['km_gps'] = round(res[vehicle]['km_gps'], 2)
                grouped_vehicle[vehicle][period_number]['viajes'] = res[vehicle]['viajes']
                grouped_vehicle[vehicle][period_number]['costo_km'] = round(res[vehicle]['costo_km'], 2)
                grouped_vehicle[vehicle][period_number]['ingreso_km'] = round(res[vehicle]['ingreso_km'], 2)
                grouped_vehicle[vehicle][period_number]['rend_gps'] = round(res[vehicle]['rend_gps'], 2)
                grouped_vehicle[vehicle][period_number]['margen'] = round(res[vehicle]['margen'], 2)
                grouped_vehicle[vehicle][period_number]['averias'] = res[vehicle]['averias']
                grouped_vehicle[vehicle][period_number]['lines'] = res[vehicle]['lines']
            period_number += 1

        # build the report
        lines = self._post_process(grouped_vehicle, options, comparison_table, line_id)
        return lines

    @api.model
    def _get_report_name(self):
        # import ipdb; ipdb.set_trace()
        return _("Trucks Report")

    def view_all_journal_items(self, options, params):
        # import ipdb; ipdb.set_trace()
        if params.get('id'):
            params['id'] = int(params.get('id').split('_')[-1])
        return self.env['tms.report'].open_journal_items(options, params)
