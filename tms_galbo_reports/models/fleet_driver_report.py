# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _

class ReportTmsFleetDriver(models.AbstractModel):
    _name = "tms.fleet.driver"
    _description = "Driver Report"
    _inherit = "tms.report"

    filter_date = {'date_from': '', 'date_to': '', 'filter': 'this_month'}
    filter_comparison = {'date_from': '', 'date_to': '', 'filter': 'no_comparison', 'number_period': 1}
    filter_all_entries = False
    filter_unfold_all = False

    def _get_templates(self):
        templates = super()._get_templates()
        templates['tms_main_table_header_template'] = 'tms_galbo_reports.template_driver_table_header'
        return templates

    def _get_columns_name(self, options):
        columns = [
            {'name': ''},
            {'name': _("Driver")},
            {'name': _("Kms GPS"), 'class': 'number'},
            {'name': _("Travels"), 'class': 'number'},
            {'name': _("Rend. GPS"), 'class': 'number'},
            {'name': _("Cost/KM"), 'class': 'number'},
            {'name': _("Incom/KM"), 'class': 'number'},
            {'name': _("Margin"), 'class': 'number'},
            {'name': _("Vel. Max. (km/h)"), 'class': 'number'},
            {'name': _("Rpm Max"), 'class': 'number'},
            {'name': _("Faults"), 'class': 'number'}, ]
        if options.get('comparison') and options['comparison'].get('periods'):
            columns += [
                {'name': _("Kms GPS"), 'class': 'number'},
                {'name': _("Travels"), 'class': 'number'},
                {'name': _("Rend. GPS"), 'class': 'number'},
                {'name': _("Cost/KM"), 'class': 'number'},
                {'name': _("Incom/KM"), 'class': 'number'},
                {'name': _("Margin"), 'class': 'number'},
                {'name': _("Vel. Max. (km/h)"), 'class': 'number'},
                {'name': _("Rpm Max"), 'class': 'number'},
                {'name': _("Faults"), 'class': 'number'},
            ] * len(options['comparison']['periods'])
        return columns

    def _get_super_columns(self, options):
        date_cols = options.get('date') and [options['date']] or []
        date_cols += (options.get('comparison') or {}).get('periods', [])
        columns = reversed(date_cols)
        return {'columns': columns, 'x_offset': 1, 'merge': 2}

    def _do_query(self, options, line_id, group_by_driver=True, limit=False):
        company = self.env['res.company'].browse(self._context.get('company_id')) or self.env['res.users']._get_company()
        params = [
            self._context.get('date_from_aml'), self._context.get('date_to'),
            self._context.get('date_from_aml'), self._context.get('date_to'),
            company.id]
        if group_by_driver:
            query = """
                SELECT
                    he.id,
                    he.name "Chofer",
                    ROUND(CAST(SUM(te.distance_real) AS decimal), 2) "Kms GPS",
                    COUNT(tt.id) "Viajes",
                    ROUND(CAST(SUM(te.distance_real) / SUM(CASE WHEN te.fuel_qty = 0 THEN 1 ELSE te.fuel_qty END) AS decimal), 2) "Rend. GPS",
                    ROUND(CAST(SUM(te.amount_total_total) / SUM(te.distance_real) AS decimal), 2) "Costo x KM",
                    ROUND(CAST(SUM(tt.amount_untaxed) / SUM(te.distance_real) AS decimal), 2) "Ingreso x KM",
                    ROUND(CAST(((SUM(tt.amount_untaxed) - SUM(te.amount_total_total)) / SUM(CASE WHEN tt.amount_untaxed = 0 THEN 1 ELSE tt.amount_untaxed END)) * 100 AS decimal) , 2) "Margen",
                    ROUND(CAST(MAX(tt.vel_max_km) AS decimal), 2) "Vel. Max. km/h",
                    ROUND(CAST(MAX(tt.rp_ms_max) AS decimal), 2) "RPM Max.",
                    COUNT(tme.id) + COALESCE(MIN(tts.paradas), 0.00) + COALESCE(MIN(ttgc.neutral), 0.00) "Incidencias"
            """
        else:
            query = """
                SELECT
                    he.id,
                    he.name "Chofer",
                    ROUND(CAST(te.distance_real AS decimal), 2) "kms_gps",
                    tt.id "viajes",
                    ROUND(CAST(te.distance_real / CASE WHEN te.fuel_qty = 0 THEN 1 ELSE te.fuel_qty END AS decimal), 2) "rend_gps",
                    ROUND(CAST(te.amount_total_total / te.distance_real AS decimal), 2) "costo_km",
                    ROUND(CAST(tt.amount_untaxed / te.distance_real AS decimal), 2) "ingreso_km",
                    ROUND(CAST(((tt.amount_untaxed - te.amount_total_total) / CASE WHEN tt.amount_untaxed = 0 THEN 1 ELSE tt.amount_untaxed END) * 100 AS decimal) , 2) "margen",
                    ROUND(CAST(tt.vel_max_km AS decimal), 2) "Vel. Max. km/h",
                    ROUND(CAST(tt.rp_ms_max AS decimal), 2) "RPM Max."
            """
        query += """
            FROM tms_travel AS tt
            JOIN tms_expense AS te ON te.id = tt.expense_id
            JOIN hr_employee AS he ON he.id = tt.employee_id
            JOIN fleet_vehicle AS fv ON fv.id = tt.unit_id
            JOIN operating_unit AS ou ON tt.operating_unit_id = ou.id
            LEFT JOIN (
                SELECT COUNT(id) "paradas", travel_id
                FROM tms_travel_stop
                WHERE address ilike ('%%huachicol%%') GROUP BY travel_id
                ) AS tts ON tts.travel_id = tt.id
            LEFT JOIN (
                SELECT COUNT(id) "neutral", travel_id
                FROM tms_travel_gear_coast
                GROUP BY travel_id
                ) AS ttgc on ttgc.travel_id = tt.id
            LEFT JOIN tms_event AS tme ON tme.travel_id = tt.id
                AND NOT tme.positive
                AND tme.type = 'driver'
                AND tme.date >= %s
                AND tme.date <= %s
            WHERE tt.date >= %s
                AND tt.date <= %s
                AND ou.company_id = %s
                AND tt.expense_id is not null
        """
        if line_id:
            query += """ AND he.id = %s"""
            params.append(line_id)
        if group_by_driver:
            query += """
                GROUP BY he.id
            """
        query += """ORDER BY he.name;"""
        self.env.cr.execute(query, tuple(params))
        results = self.env.cr.fetchall()
        return results

    def _do_query_group_by_driver(self, options, line_id):
        # import ipdb; ipdb.set_trace()
        results = self._do_query(options, line_id, group_by_driver=True, limit=False)
        used_currency = self.env.user.company_id.currency_id
        company = self.env['res.company'].browse(self._context.get('company_id')) or self.env['res.users']._get_company()
        date = self._context.get('date_to') or fields.Date.today()
        def build_converter(currency):
            def convert(amount):
                return currency._convert(amount, used_currency, company, date)
            return convert

        compute_table = {
            a.id: build_converter(a.company_id.currency_id)
            for a in self.env['hr.employee'].browse([k[0] for k in results])
        }
        results = dict([(
            k[0], {
                'km_gps': compute_table[k[0]](k[2]) if k[0] in compute_table else k[2],
                'viajes': k[3],
                'rend_gps': compute_table[k[0]](k[4]) if k[0] in compute_table else k[4],
                'costo_km': compute_table[k[0]](k[5]) if k[0] in compute_table else k[5],
                'ingreso_km': compute_table[k[0]](k[6]) if k[0] in compute_table else k[6],
                'margen': compute_table[k[0]](k[7]) if k[0] in compute_table else k[7],
                'vel_max': k[8],
                'rpm_max': k[9],
                'averias': k[10],
            }
        ) for k in results])
        return results

    def _group_by_driver_id(self, options, line_id):
        drivers = {}
        results = self._do_query_group_by_driver(options, line_id)
        context = self.env.context

        for driver_id, result in results.items():
            driver = self.env['hr.employee'].browse(driver_id)
            drivers[driver] = result

            travel_ids = self._do_query(options, driver.id, group_by_driver=False)

            drivers[driver]['total_lines'] = len(travel_ids)
            offset = int(options.get('lines_offset', 0))
            if self.MAX_LINES:
                stop = offset + self.MAX_LINES
            else:
                stop = None
            if not context.get('print_mode'):
                travel_ids = travel_ids[offset:stop]

            drivers[driver]['lines'] = travel_ids

        return drivers

    def _post_process(self, grouped_driver, options, comparison_table, line_id):
        lines = []
        context = self.env.context
        company_id = context.get('company_id') or self.env.user.company_id

        sorted_driver = sorted(grouped_driver, key=lambda a: a.name)
        unfold_all = context.get('print_mode') and len(options.get('unfolded_lines')) == 0
        col_total = {}
        for driver in sorted_driver:
            display_name = driver.name
            cols = []
            travels_lines = []
            for period in range(len(comparison_table)):
                km_gps = grouped_driver[driver][period]['km_gps']
                viajes = grouped_driver[driver][period]['viajes']
                costo_km = grouped_driver[driver][period]['costo_km']
                ingreso_km = grouped_driver[driver][period]['ingreso_km']
                rend_gps = grouped_driver[driver][period]['rend_gps']
                margen = grouped_driver[driver][period]['margen']
                vel_max = grouped_driver[driver][period]['vel_max']
                rpm_max = grouped_driver[driver][period]['rpm_max']
                averias = grouped_driver[driver][period]['averias']

                if period not in col_total:
                    col_total[period] = {
                        'km_gps': 0, 'viajes': 0, 'costo_km': 0,
                        'ingreso_km': 0, 'rend_gps': 0, 'margen': 0,
                        'vel_max': 0, 'rpm_max': 0, 'averias': 0}

                col_total[period]['km_gps'] += km_gps
                col_total[period]['viajes'] += viajes
                col_total[period]['averias'] += averias

                cols += [
                    {'name': km_gps}, {'name': viajes}, {'name': rend_gps},
                    {'name': costo_km}, {'name': ingreso_km}, {'name': margen},
                    {'name': vel_max}, {'name': rpm_max}, {'name': averias},
                ]

                if 'driver_%s' % (driver.id,) in options.get('unfolded_lines') or unfold_all:
                    for travel in grouped_driver[driver][period]['lines']:
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
                        columns += [{'name': ''} for v in range(9 * period)]
                        columns += [{'name': v} for v in [
                            travel[2], travel_id.name, travel[4],
                            travel[5], travel[6], travel[7], travel[8],
                            travel[9]]]
                        columns[0]['class'] = 'whitespace_print'
                        columns[0]['title'] = name_title
                        line_value = {
                            'id': travel_id.id,
                            'action_context': action_context,
                            'caret_options': caret_type,
                            'class': 'top-vertical-align',
                            'parent_id': 'driver_%s' % (driver.id,),
                            'name': travel_id.name if travel_id.name else '/',
                            'columns': columns,
                            'level': 4,
                        }
                        travels_lines.append(line_value)

            lines.append({
                'id': 'driver_%s' % (driver.id,),
                'name': len(display_name) > 40 and not context.get('print_mode') and display_name[:40]+'...' or display_name,
                'title_hover': display_name,
                'columns': cols,
                'level': 2,
                'unfoldable': True,
                'unfolded': 'driver_%s' % (driver.id,) in options.get('unfolded_lines') or unfold_all,
                'colspan': 2,
            })

            if 'driver_%s' % (driver.id,) in options.get('unfolded_lines') or unfold_all:
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

    @api.model
    def _get_lines(self, options, line_id=None):
        lines = []
        grouped_driver = {}
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
            )._group_by_driver_id(options, line_id)

            for driver in res:
                if driver not in grouped_driver:
                    grouped_driver[driver] = [
                        {
                            'km_gps': 0, 'viajes': 0, 'rend_gps': 0,
                            'costo_km': 0, 'ingreso_km': 0, 'margen': 0,
                            'vel_max': 0, 'rpm_max': 0, 'averias': 0,
                            'lines': []} for p in comparison_table]
                grouped_driver[driver][period_number]['km_gps'] = round(res[driver]['km_gps'], 2)
                grouped_driver[driver][period_number]['viajes'] = res[driver]['viajes']
                grouped_driver[driver][period_number]['rend_gps'] = round(res[driver]['rend_gps'], 2)
                grouped_driver[driver][period_number]['costo_km'] = round(res[driver]['costo_km'], 2)
                grouped_driver[driver][period_number]['ingreso_km'] = round(res[driver]['ingreso_km'], 2)
                grouped_driver[driver][period_number]['margen'] = round(res[driver]['margen'], 2)
                grouped_driver[driver][period_number]['vel_max'] = res[driver]['vel_max']
                grouped_driver[driver][period_number]['rpm_max'] = res[driver]['rpm_max']
                grouped_driver[driver][period_number]['averias'] = res[driver]['averias']
                grouped_driver[driver][period_number]['lines'] = res[driver]['lines']
            period_number += 1

        # build the report
        lines = self._post_process(grouped_driver, options, comparison_table, line_id)
        return lines

    @api.model
    def _get_report_name(self):
        return _("Drivers Report")
