# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _

class ReportTmsFleetCustomer(models.AbstractModel):
    _name = "tms.fleet.customer"
    _description = "Customer Report"
    _inherit = "tms.report"

    filter_date = {'date_from': '', 'date_to': '', 'filter': 'this_month'}
    filter_comparison = {'date_from': '', 'date_to': '', 'filter': 'no_comparison', 'number_period': 1}
    filter_all_entries = False
    filter_unfold_all = False

    def _get_templates(self):
        templates = super()._get_templates()
        templates['tms_main_table_header_template'] = 'tms_galbo_reports.template_customer_table_header'
        return templates

    def _get_columns_name(self, options):
        columns = [
            {'name': ''},
            {'name': _("Customer")},
            {'name': _("Kms GPS"), 'class': 'number'},
            {'name': _("Travels"), 'class': 'number'},
            {'name': _("Total Income"), 'class': 'number'},
            {'name': _("Margin"), 'class': 'number'},
            {'name': _("Current Balance"), 'class': 'number'},
            {'name': _("Balance Due"), 'class': 'number'},
            {'name': _("Portfolio days"), 'class': 'number'}, ]
        if options.get('comparison') and options['comparison'].get('periods'):
            columns += [
                {'name': _("Kms GPS"), 'class': 'number'},
                {'name': _("Travels"), 'class': 'number'},
                {'name': _("Total Income"), 'class': 'number'},
                {'name': _("Margin"), 'class': 'number'},
                {'name': _("Current Balance"), 'class': 'number'},
                {'name': _("Balance Due"), 'class': 'number'},
                {'name': _("Portfolio days"), 'class': 'number'},
            ] * len(options['comparison']['periods'])
        return columns

    def _get_super_columns(self, options):
        date_cols = options.get('date') and [options['date']] or []
        date_cols += (options.get('comparison') or {}).get('periods', [])
        columns = reversed(date_cols)
        return {'columns': columns, 'x_offset': 1, 'merge': 2}

    def _do_query(self, options, line_id, group_by_customer=True, limit=False):
        company = self.env['res.company'].browse(self._context.get('company_id')) or self.env['res.users']._get_company()
        params = [
            self._context.get('date_from_aml'),
            self._context.get('date_to'),
            company.id]
        if group_by_customer:
            query = """
                SELECT
                    rp.id,
                    rp.name "Cliente",
                    ROUND(CAST(SUM(te.distance_real) AS decimal), 2) "Kms GPS",
                    COUNT(tt.id) "Viajes",
                    ROUND(CAST(SUM(tt.amount_untaxed )AS decimal), 2) "Ingreso total",
                    ROUND(CAST(((SUM(tt.amount_untaxed) - SUM(te.amount_total_total)) / SUM(CASE WHEN tt.amount_untaxed = 0 THEN 1 ELSE tt.amount_untaxed END)) * 100 AS decimal) , 2) "Margen",
                    ROUND(CAST(COALESCE(MIN(invoices.saldo), 0.00) AS decimal), 2) "Saldo actual",
                    ROUND(CAST(COALESCE(MIN(vencidas.vencido), 0.00) AS decimal), 2) "Vencido actual",
                    COALESCE(MIN(dias_cartera.dias_cartera), 0) "Dias Cartera"
            """
        else:
            query = """
                SELECT
                    rp.id,
                    rp.name "Cliente",
                    ROUND(CAST(te.distance_real AS decimal), 2) "Kms GPS",
                    tt.id "Viajes",
                    ROUND(CAST(tt.amount_untaxed AS decimal), 2) "Ingreso total",
                    ROUND(CAST(((tt.amount_untaxed - te.amount_total_total) / CASE WHEN tt.amount_untaxed = 0 THEN 1 ELSE tt.amount_untaxed END) * 100 AS decimal) , 2) "Margen"
            """
        query += """
            FROM tms_travel AS tt
            JOIN tms_expense AS te ON te.id = tt.expense_id
            JOIN res_partner AS rp ON rp.id = tt.partner_id
            JOIN fleet_vehicle AS fv ON fv.id = tt.unit_id
            JOIN operating_unit AS ou ON tt.operating_unit_id = ou.id
        """
        if group_by_customer:
            query += """
                LEFT JOIN (
                    SELECT SUM(residual) "vencido", partner_id
                    FROM account_invoice WHERE state = 'open'
                    AND type = 'out_invoice' AND (date_due < now())
                    GROUP BY partner_id) AS vencidas ON vencidas.partner_id = tt.partner_id
                LEFT JOIN (
                    SELECT SUM(residual) "saldo", partner_id
                    FROM account_invoice WHERE state = 'open'
                    AND type = 'out_invoice'
                    GROUP BY partner_id) AS invoices ON invoices.partner_id = tt.partner_id
                LEFT JOIN (
                    SELECT
                        partner_id,
                        COALESCE((SUM(facturas_pago.elapsed_days) / COUNT(facturas_pago.facturas)), 0) "dias_cartera"
                    FROM (
                        SELECT
                            ai.id "facturas",
                            max(amlcre.date) - min(aml.date) "elapsed_days",
                            ai.partner_id
                        FROM account_invoice AS ai
                        JOIN account_move_line AS aml ON aml.invoice_id = ai.id
                        JOIN account_account AS aa ON aa.id = aml.account_id
                            AND aa.internal_type = 'receivable'
                        JOIN account_partial_reconcile AS apr ON apr.debit_move_id = aml.id
                        JOIN account_move_line AS amlcre ON amlcre.id = apr.credit_move_id
                        WHERE ai.state = 'paid'
                          AND ai.date_invoice >= CAST(%s AS date) - interval '1 year'
                          AND ai.date_invoice <= %s
                          AND ai.company_id = %s
                        GROUP BY ai.id) AS facturas_pago
                    GROUP BY facturas_pago.partner_id) AS dias_cartera ON dias_cartera.partner_id = tt.partner_id
            """
            params.insert(0, self._context.get('date_to'))
            params.insert(1, self._context.get('date_to'))
            params.insert(2, company.id)
        query += """
            WHERE tt.date >= %s
            AND tt.date <= %s
            AND ou.company_id = %s
            AND tt.expense_id IS NOT NULL
        """
        if line_id:
            query += """ AND rp.id = %s"""
            params.append(line_id)
        if group_by_customer:
            query += """
                GROUP BY rp.id
            """
        query += """ORDER BY rp.name;"""
        self.env.cr.execute(query, tuple(params))
        results = self.env.cr.fetchall()
        return results

    def _do_query_group_by_customer(self, options, line_id):
        # import ipdb; ipdb.set_trace()
        results = self._do_query(options, line_id, group_by_customer=True, limit=False)
        used_currency = self.env.user.company_id.currency_id
        company = self.env['res.company'].browse(self._context.get('company_id')) or self.env['res.users']._get_company()
        date = self._context.get('date_to') or fields.Date.today()
        def build_converter(currency):
            def convert(amount):
                return currency._convert(amount, used_currency, company, date)
            return convert

        compute_table = {
            a.id: build_converter(a.company_id.currency_id)
            for a in self.env['res.partner'].browse([k[0] for k in results])
        }
        results = dict([(
            k[0], {
                'km_gps': compute_table[k[0]](k[2]) if k[0] in compute_table else k[2],
                'viajes': k[3],
                'total_inc': compute_table[k[0]](k[4]) if k[0] in compute_table else k[4],
                'margen': k[5],
                'cur_bal': compute_table[k[0]](k[6]) if k[0] in compute_table else k[6],
                'due_bal': compute_table[k[0]](k[7]) if k[0] in compute_table else k[7],
                'dias': k[8],
            }
        ) for k in results])
        return results

    def _group_by_customer_id(self, options, line_id):
        customers = {}
        results = self._do_query_group_by_customer(options, line_id)
        context = self.env.context

        for customer_id, result in results.items():
            customer = self.env['res.partner'].browse(customer_id)
            customers[customer] = result

            travel_ids = self._do_query(options, customer.id, group_by_customer=False)

            customers[customer]['total_lines'] = len(travel_ids)
            offset = int(options.get('lines_offset', 0))
            if self.MAX_LINES:
                stop = offset + self.MAX_LINES
            else:
                stop = None
            if not context.get('print_mode'):
                travel_ids = travel_ids[offset:stop]

            customers[customer]['lines'] = travel_ids

        return customers

    def _post_process(self, grouped_customer, options, comparison_table, line_id):
        lines = []
        context = self.env.context
        company_id = context.get('company_id') or self.env.user.company_id

        sorted_customer = sorted(grouped_customer, key=lambda a: a.name)
        unfold_all = context.get('print_mode') and len(options.get('unfolded_lines')) == 0
        col_total = {}
        for customer in sorted_customer:
            display_name = customer.name
            cols = []
            travels_lines = []
            for period in range(len(comparison_table)):
                km_gps = grouped_customer[customer][period]['km_gps']
                viajes = grouped_customer[customer][period]['viajes']
                total_inc = grouped_customer[customer][period]['total_inc']
                margen = grouped_customer[customer][period]['margen']
                cur_bal = grouped_customer[customer][period]['cur_bal']
                due_bal = grouped_customer[customer][period]['due_bal']
                dias = grouped_customer[customer][period]['dias']

                if period not in col_total:
                    col_total[period] = {
                        'km_gps': 0, 'viajes': 0, 'total_inc': 0,
                        'cur_bal': 0, 'due_bal': 0}

                col_total[period]['km_gps'] += km_gps
                col_total[period]['viajes'] += viajes
                col_total[period]['total_inc'] += total_inc
                col_total[period]['cur_bal'] += cur_bal
                col_total[period]['due_bal'] += due_bal

                cols += [
                    {'name': km_gps}, {'name': viajes}, {'name': total_inc},
                    {'name': margen}, {'name': cur_bal}, {'name': due_bal},
                    {'name': dias},
                ]

                if 'customer_%s' % (customer.id,) in options.get('unfolded_lines') or unfold_all:
                    for travel in grouped_customer[customer][period]['lines']:
                        travel_id = self.env['tms.travel'].browse([travel[3]])
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
                            travel[2], travel_id.name,
                            travel[4], travel[5]]]
                        columns[0]['class'] = 'whitespace_print'
                        columns[0]['title'] = name_title
                        line_value = {
                            'id': travel_id.id,
                            'action_context': action_context,
                            'caret_options': caret_type,
                            'class': 'top-vertical-align',
                            'parent_id': 'customer_%s' % (customer.id,),
                            'name': travel_id.name if travel_id.name else '/',
                            'columns': columns,
                            'level': 4,
                        }
                        travels_lines.append(line_value)

            lines.append({
                'id': 'customer_%s' % (customer.id,),
                'name': len(display_name) > 40 and not context.get('print_mode') and display_name[:40]+'...' or display_name,
                'title_hover': display_name,
                'columns': cols,
                'level': 2,
                'unfoldable': True,
                'unfolded': 'customer_%s' % (customer.id,) in options.get('unfolded_lines') or unfold_all,
                'colspan': 2,
            })

            if 'customer_%s' % (customer.id,) in options.get('unfolded_lines') or unfold_all:
                lines += travels_lines

        if not line_id:
            col = [{'name': ''}]
            for period in col_total:
                # for key in col_total[period]:
                col.append({'name': col_total[period]['km_gps']})
                col.append({'name': col_total[period]['viajes']})
                col.append({'name': col_total[period]['total_inc']})
                col.append({'name': ''})
                col.append({'name': col_total[period]['cur_bal']})
                col.append({'name': col_total[period]['due_bal']})
                col.append({'name': ''})
            lines.append({
                'id': 'general_ledger_total_%s' % company_id.id,
                'name': _('Total'),
                'class': 'total',
                'level': 1,
                'columns': col,
            })
        return lines

    @api.model
    def _get_lines(self, options, line_id=None):
        lines = []
        grouped_customer = {}
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
            )._group_by_customer_id(options, line_id)

            for customer in res:
                if customer not in grouped_customer:
                    grouped_customer[customer] = [
                        {
                            'km_gps': 0, 'viajes': 0, 'total_inc': 0,
                            'margen': 0, 'cur_bal': 0, 'due_bal': 0,
                            'dias': 0, 'lines': []} for p in comparison_table]
                grouped_customer[customer][period_number]['km_gps'] = round(res[customer]['km_gps'], 2)
                grouped_customer[customer][period_number]['viajes'] = res[customer]['viajes']
                grouped_customer[customer][period_number]['total_inc'] = round(res[customer]['total_inc'], 2)
                grouped_customer[customer][period_number]['margen'] = round(res[customer]['margen'], 2)
                grouped_customer[customer][period_number]['cur_bal'] = round(res[customer]['cur_bal'], 2)
                grouped_customer[customer][period_number]['due_bal'] = round(res[customer]['due_bal'], 2)
                grouped_customer[customer][period_number]['dias'] = res[customer]['dias']
                grouped_customer[customer][period_number]['lines'] = res[customer]['lines']
            period_number += 1

        # build the report
        lines = self._post_process(grouped_customer, options, comparison_table, line_id)
        return lines

    @api.model
    def _get_report_name(self):
        return _("Customer Report")
