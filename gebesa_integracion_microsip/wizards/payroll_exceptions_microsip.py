# Copyright 2022, Cesar Barron
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import timedelta
import fdb


class PrepayrollOpenMicrosip(models.TransientModel):
    _name = 'prepayroll.open.microsip'
    _description = 'Opens a new payroll in Microsip'

    date_start = fields.Date(
        string='Date start'
    )
    date_end = fields.Date(
        string='Date end'
    )
    union_dues = fields.Boolean(
        string='Apply union dues',
    )

    def _get_overlaping_days(self, d1, d2):
        delta = d2 - d1
        return set([d1 + timedelta(days=i) for i in range(delta.days + 1)])

    def _get_seventh_day(self, leaves):
        seventh_day = 7
        if leaves == 1:
            seventh_day = 5.83
        if leaves == 2:
            seventh_day = 4.67
        if leaves == 3:
            seventh_day = 3.5
        if leaves == 4:
            seventh_day = 2.33
        if leaves == 5:
            seventh_day = 1.17

        return seventh_day

    def _get_connection(self):
        db_m = self.env.user.company_id.db_microsip
        user = self.env.user.company_id.user_microsip
        passw = self.env.user.company_id.pass_microsip
        host = self.env.user.company_id.host_microsip
        port = self.env.user.company_id.port_microsip

        if not db_m:
            raise ValidationError(_("Please specify a microsip database \
                for the company"))
        if not user:
            raise ValidationError(_("Please specify a microsip user \
                for the company"))
        if not passw:
            raise ValidationError(_("Please specify a microsip password \
                for the company"))
        if not host:
            raise ValidationError(_("Please specify a microsip host \
                for the company"))
        if not port:
            raise ValidationError(_("Please specify a microsip port \
                for the company"))

        con = fdb.connect(
            host=host, database=db_m, port=port,
            user=user, password=passw, charset='WIN1251')

        return con

    def _get_valid_attendance_incidents(self, time_type=None, employee_id=None, working_weekdays=None, only_for_paid=False):
        leaves = self._get_leaves_in_period(time_type, employee_id, only_for_paid)
        leave_days_current_week = []
        for leave in leaves:
            overlap_days = self._get_overlaping_days(
                self.date_start, self.date_end) & self._get_overlaping_days(
                leave.request_date_from, leave.request_date_to)
            leave_days_current_week += ([i for i in overlap_days])

        valid_leaves = []
        for day in leave_days_current_week:
            if str(day.weekday()) in working_weekdays:
                valid_leaves.append(day)
        return valid_leaves

    def _set_vacation(self, employee_id, con, cur):
        leaves = self._get_leaves_in_period('vacation', employee_id.id)
        emp = employee_id.id_microsip
        for vacation in leaves:
            date_from = vacation.request_date_from.strftime("%d.%m.%Y")

            cur.execute("""
                SELECT VACACIONES_ID
                FROM VACACIONES
                WHERE EMPLEADO_ID = ? AND FECHA_INICIAL = ?
            """, (emp, date_from))
            result = cur.fetchall()
            if result:
                continue

            cur.execute("SELECT MAX(VACACIONES_ID) + 1 FROM VACACIONES")
            id_vac = cur.fetchall()[0][0]

            cur.execute("""
                INSERT INTO VACACIONES(
                    VACACIONES_ID,
                    EMPLEADO_ID,
                    FECHA_INICIAL,
                    DIAS,
                    DESCRIPCION,

                    ESTATUS,
                    USUARIO_CREADOR,
                    FECHA_HORA_CREACION,
                    USUARIO_AUT_MODIF)
                    VALUES (?, ?, ?, ?, ?, 'A', 'ODOO', ?, 'ODOO')
                """, (id_vac, emp, date_from, vacation.number_of_days_display,
                      vacation.name, fields.Date.today().strftime("%d.%m.%Y")))
            con.commit()

    def _set_leaves(self, employee_id, leaves, con, cur):
        for leave in leaves:
            cur.execute("""
                SELECT INCIDENCIA_ASISTENCIA_ID
                FROM INCIDENCIAS_ASISTENCIAS
                WHERE EMPLEADO_ID = ? AND FECHA = ?
            """, (employee_id, leave.strftime("%d.%m.%Y")))
            result = cur.fetchall()
            if result:
                continue

            cur.execute("""
                SELECT MAX(INCIDENCIA_ASISTENCIA_ID) + 1
                FROM INCIDENCIAS_ASISTENCIAS""")
            id_inc_asi = cur.fetchall()[0][0]

            cur.execute("""
                INSERT INTO INCIDENCIAS_ASISTENCIAS(
                    INCIDENCIA_ASISTENCIA_ID,
                    EMPLEADO_ID,
                    TIPO,
                    FECHA,

                    TIPO_PERMISO,
                    HORAS_EXT,
                    ESTATUS_HORAS_EXTRAS,
                    HORAS_FALTAS,


                    OBSERVACIONES,
                    USUARIO_CREADOR,
                    FECHA_HORA_CREACION,
                    USUARIO_AUT_MODIF)
                    VALUES (?, ?, ?, ?, NULL, NULL, NULL, NULL, ?, 'ODOO', ?, 'ODOO')
                """, (id_inc_asi, employee_id, 'F', leave.strftime("%d.%m.%Y"),
                      'Falta', fields.Date.today().strftime("%d.%m.%Y")))
            con.commit()

    def _set_inhability(self, employee_id, con, cur):
        leaves = self._get_leaves_in_period('inhability', employee_id.id)
        emp = employee_id.id_microsip

        for inhability in leaves:
            date = inhability.request_date_from.strftime("%d.%m.%Y")

            cur.execute("""
                SELECT INCAPACIDAD_ID
                FROM INCAPACIDADES
                WHERE EMPLEADO_ID = ? AND FECHA = ?
            """, (emp, date))
            result = cur.fetchall()
            if result:
                continue

            cur.execute("""
                SELECT MAX(INCAPACIDAD_ID) + 1
                FROM INCAPACIDADES""")
            id_inc = cur.fetchall()[0][0]
            # import ipdb; ipdb.set_trace()
            cur.execute("""
                INSERT INTO INCAPACIDADES(
                    INCAPACIDAD_ID,
                    EMPLEADO_ID,
                    FECHA,
                    RAMO,
                    TIPO_RIESGO,

                    SECUELA,
                    FOLIO,
                    DIAS,
                    CONTROL_INCAP,
                    PORCENTAJE,
                    DESCRIPCION,

                    USUARIO_CREADOR,
                    FECHA_HORA_CREACION,
                    USUARIO_AUT_MODIF)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'ODOO', ?, 'ODOO')
                """, (id_inc, emp, date, inhability.ramo_seguro,
                      inhability.tipo_riesgo, inhability.secuela,
                      inhability.incapacidad_folio, int(inhability.number_of_days_display),
                      inhability.control, inhability.porcentaje,
                      inhability.name, fields.Date.today().strftime("%d.%m.%Y")))
            con.commit()

    def _set_payroll_exceptions(self, empleados, nomina):
        con = self._get_connection()
        cur = con.cursor()

        for emp in empleados:

            employee = self.env['hr.employee'].search([
                ('id_microsip', '=', emp)], limit=1)

            attendances = self._get_attendances_in_period(employee.id)

            working_weekdays = tuple(set(employee.resource_calendar_id.attendance_ids.mapped('dayofweek')))

            # Numero de días de Faltas
            valid_leaves = self._get_valid_attendance_incidents(
                'leave',
                employee.id,
                working_weekdays)
            leaves_paid = self._get_valid_attendance_incidents(
                'leave',
                employee.id,
                working_weekdays,
                True)
            # if valid_leaves:
            #     self._set_leaves(emp, valid_leaves, con, cur)

            # Numero de días de Vacaciones
            valid_vacations = self._get_valid_attendance_incidents(
                'vacation',
                employee.id,
                working_weekdays)
            vacations_paid = self._get_valid_attendance_incidents(
                'vacation',
                employee.id,
                working_weekdays,
                True)
            if valid_vacations:
                self._set_vacation(employee, con, cur)

            # Numero de días de Incapacidades
            valid_inhabilities = self._get_valid_attendance_incidents(
                'inhability',
                employee.id,
                working_weekdays)
            if valid_inhabilities:
                self._set_inhability(employee, con, cur)

            # Numero de horas extra
            assigns_overtime = self._get_salary_assignments_exceptions(employee.id_microsip, True)
            qty_overtime = int(sum(map(lambda x: x['qty'], assigns_overtime)))
            amount_overtime = sum(map(lambda x: x['amount'] * x['qty'], assigns_overtime))

            num_of_leaves = len(valid_leaves)
            num_of_leaves_paid = len(leaves_paid)
            num_of_vacations = len(valid_vacations)
            num_of_vacations_paid = len(vacations_paid)
            num_of_inhabilities = len(valid_inhabilities)
            num_of_atten = len(attendances)

            total_day = num_of_leaves + (num_of_vacations - num_of_vacations_paid) + num_of_inhabilities + num_of_atten
            if total_day < 6:
                num_of_atten += 6 - total_day

            seventh_day = self._get_seventh_day(num_of_leaves)
            if num_of_vacations > 0:
                seventh_day -= (num_of_vacations - num_of_vacations_paid)

            print(str(num_of_leaves))
            print(str(num_of_vacations))
            print(str(num_of_inhabilities))
            print(str(num_of_atten))
            print(str(qty_overtime))
            print(str(amount_overtime))

            payslip = self.env['hr.payslip'].sudo().create({
                'employee_id': employee.id,
                'date_from': self.date_start,
                'date_to': self.date_end,
                'holidays': num_of_vacations,
                'days_disability': num_of_inhabilities,
                'unjustified_absences': num_of_leaves - num_of_leaves_paid,
                'excused_absences': leaves_paid,
                'paid': self.union_dues
            })

            cur.execute("""
                SELECT EXCEP_EMP_ID
                FROM EXCEP_EMPLEADOS
                WHERE NOMINA_ID = ? AND EMPLEADO_ID = ?
            """, (nomina, emp))
            resu = cur.fetchall()
            nomemp_excep = False
            if resu:
                nomemp_excep = resu[0][0]
            if nomemp_excep:
                continue

            cur.execute("""
                SELECT MAX(EXCEP_EMP_ID) + 1
                FROM EXCEP_EMPLEADOS
            """)
            id_excep = cur.fetchall()[0][0]

            cur.execute("""
                    INSERT INTO EXCEP_EMPLEADOS(
                        EXCEP_EMP_ID,
                        NOMINA_ID,
                        EMPLEADO_ID,
                        SEPTIMO_DIA,
                        DIAS_HRS_PAGAR,
                        DIAS_HRS_PAGAR_A7,
                        DIAS_VAC,
                        DIAS_A_COT,
                        FALTAS,
                        FALTAS_A7,
                        IMPORTE_FALTAS,
                        DIAS_AUS_IMSS,
                        DIAS_INCAP,
                        INCAP_TOTAL,
                        HORAS_EXT,
                        DIAS_EXT,
                        IMPORTE_HORAS_EXT,
                        HORAS_ESP,
                        DIAS_ESP,
                        IMPORTE_HORAS_ESP,
                        CAUSA_BAJA,
                        DIAS_BASE_INDEM,
                        DIAS_ANTIG_INDEM,
                        DIAS_PRIMER_INDEM,
                        USUARIO_CREADOR,
                        USUARIO_ULT_MODIF)
                        VALUES (?, ?, ?, 'S', ?, ?, ?, 007.75, '00000',
                        ?, 0000000000000.00,
                        0, ?, 'N', ?, 3.00, ?, '0000', 0, 0000000000000.00,
                        NULL, 000.00, 000.00, 000.00, 'ODOO', 'ODOO')
                    """, (id_excep, nomina, emp, seventh_day, num_of_atten,
                          num_of_vacations, '{:05d}'.format(num_of_leaves * 1000),
                          num_of_inhabilities, '{:04d}'.format(qty_overtime * 100),
                          amount_overtime))
            con.commit()
            new_dets = self._set_payroll_exceptions_det(id_excep, emp, payslip, con, cur)
        con.close()

        return

    def _set_payroll_exceptions_det(self, exception_id=None, employee_id=None, payslip_id=None, con=None, cur=None):
        structure_lines = self._get_payroll_structure_exceptions(employee_id, payslip_id)
        assigns_lines = self._get_salary_assignments_exceptions(employee_id, False)
        total_lines = structure_lines + assigns_lines
        created_exdet = []
        for line in total_lines:
            if int(line['microsip_rule_id']) < 1:
                continue

            cur.execute("""
                SELECT MAX(EXCEP_EMP_DET_ID) + 1
                FROM EXCEP_EMPLEADOS_DET
            """)
            next_id = cur.fetchall()[0][0]

            cur.execute("""
                INSERT INTO EXCEP_EMPLEADOS_DET(
                    EXCEP_EMP_DET_ID,
                    EXCEP_EMP_ID,
                    CONCEPTO_NO_ID,
                    CUOTA,
                    SUBEM_CAUSADO,
                    AHORRO_EMPRESA,
                    ISR_INDEM,
                    ACTIVO,
                    ES_PERIODICO)
                    VALUES (?, ?, ?, ?, 0.0, 0.0, 0.0, 'S', 'S')
                """, (next_id, exception_id, line['microsip_rule_id'], line['amount'] * line['qty']))
            con.commit()
            created_exdet.append(next_id)
        return created_exdet

    def _get_payroll_structure_exceptions(self, employee_id, payslip_id):

        # class BrowsableObject(object):
        #     def __init__(self, employee_id, dict, env):
        #         self.employee_id = employee_id
        #         self.dict = dict
        #         self.env = env

        #     def __getattr__(self, attr):
        #         return attr in self.dict and self.dict.__getitem__(attr) or 0.0

        # class Payslips(BrowsableObject):
        #     '''a class that will be used into the python code, mainly for usability purposes'''

        #     def sum(self, code, from_date, to_date=None):
        #         if to_date is None:
        #             to_date = fields.Date.today()
        #         self.env.cr.execute("""SELECT sum(case when hp.credit_note = False then (pl.total) else (-pl.total) end)
        #                     FROM hr_payslip as hp, hr_payslip_line as pl
        #                     WHERE hp.employee_id = %s AND hp.state = 'done'
        #                     AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pl.slip_id AND pl.code = %s""",
        #                     (self.employee_id, from_date, to_date, code))
        #         res = self.env.cr.fetchone()
        #         return res and res[0] or 0.0

        employee = self.env['hr.employee'].search([
            ('id_microsip', '=', employee_id)], limit=1)

        if not employee:
            return []

        contract = employee.contract_id

        if not contract:
            return

        # payslip = self.env['hr.payslip'].sudo().create({
        #     'employee_id': employee.id,
        #     'date_from': self.date_start,
        #     'date_to': self.date_end,
        # })
        # payslips = Payslips(payslip.employee_id.id, payslip, self.env)
        # baselocaldict = {'payslip': payslips}

        structure = contract.struct_id
        lines = []
        # localdict = dict({}, employee=employee, contract=contract)
        localdict = dict({}, employee=employee, contract=contract, payslip=payslip_id)
        for rule in structure.rule_ids.filtered(lambda x: not x.type_overtime_hours):
            localdict['result'] = None
            localdict['result_qty'] = 1.0
            localdict['result_rate'] = 100
            if rule._satisfy_condition(localdict) and rule.id:
                amount, qty, rate = rule._compute_rule(localdict)
                print('amount: ' + str(amount))
                print('qty: ' + str(qty))
                print('rate: ' + str(rate))
                line = {
                    'odoo_rule_id': rule.id,
                    'microsip_rule_id': rule.id_microsip,
                    'employee_id': employee_id,
                    'qty': qty,
                    'amount': amount,
                    'rate': rate,
                    'description': rule.code + ' - ' + rule.name
                }
                lines.append(line)
        return lines

    def fix_overtime_assingments(self, employee_id):
        leaves_starting = self.env['hr.leave'].sudo().search([
            ('request_date_from', '>=', self.date_start),
            ('request_date_from', '<=', self.date_end),
            ('time_type', '=', 'leave'),
            ('employee_id', '=', employee_id)
        ]).ids

        if not leaves_starting:
            return

        rule_overtime = self.env.ref('to_attendance_device.horas_extras')
        rule_basic = self.env.ref('hr_payroll.hr_rule_basic')

        domain = [
            ('employee_id', '=', employee_id),
            ('date_assing', '>=', self.date_start),
            ('date_assing', '<=', self.date_end)]

        assign_overtime = self.env['hr.salary.assingments'].search(domain + [
            ('salary_rule_id', '=', rule_overtime.id)])

        if not assign_overtime or assign_overtime.quantity < 7:
            return

        hours = assign_overtime.quantity - 6
        assign_overtime.write({
            'quantity': 6,
            'note': 'Tiempo Extra: 6 hora(s)',
        })

        assign_basic_overtime = self.env['hr.salary.assingments'].search(
            domain + [
                ('salary_rule_id', '=', rule_basic.id),
                ('date_assing', '=', assign_overtime.date_assing),
                ('note', 'like', 'Tiempo Extra 2: ')])

        if assign_basic_overtime:
            new_qty = assign_basic_overtime.quantity + hours
            assign_basic_overtime.write({
                'quantity': new_qty,
                'note': 'Tiempo Extra: ' + str(new_qty) + ' hora(s)',
            })
        else:
            new_assing = self.env['hr.salary.assingments'].create({
                'employee_id': employee_id,
                'contract_id': assign_overtime.contract_id.id,
                'name': 'Tiempo Extra 2',
                'quantity': hours,
                'amount': assign_overtime.contract_id.salario_hora * 2,
                'note': 'Tiempo Extra 2: ' + str(hours) + ' hora(s)',
                'salary_rule_id': rule_basic.id,
                'date_assing': assign_overtime.date_assing,
                'date_paid': assign_overtime.date_paid,
            })
            if assign_overtime.state == 'validated':
                new_assing.validate()

    def _get_salary_assignments_exceptions(self, employee_id, overtime):
        employee = self.env['hr.employee'].search([
            ('id_microsip', '=', employee_id)], limit=1)

        if not employee:
            return []

        self.fix_overtime_assingments(employee.id)

        domain = [
            ('employee_id', '=', employee.id),
            ('date_assing', '>=', self.date_start),
            ('date_assing', '<=', self.date_end),
            ('amount', '>', 0.00),
            ('state', '=', 'validated')]

        salary_assignments = self.env['hr.salary.assingments'].search(domain)

        lines = []
        for assign in salary_assignments:
            # No se consideran horas extra Si overtime es igual a false
            if assign.salary_rule_id.type_overtime_hours and not overtime:
                continue

            # Solor se consideran horas extra Si overtime es igual a true
            if not assign.salary_rule_id.type_overtime_hours and overtime:
                continue

            if not assign.salary_rule_id.id_microsip:
                continue

            line = {
                'odoo_rule_id': assign.salary_rule_id.id,
                'microsip_rule_id': assign.salary_rule_id.id_microsip,
                'employee_id': employee_id,
                'qty': assign.quantity,
                'amount': assign.amount,
                'rate': assign.rate,
                'description': assign.note,
            }

            lines.append(line)
        return lines

    def _get_last_payroll_id_from_ms(self):
        con = self._get_connection()
        cur = con.cursor()

        cur.execute("""
            SELECT FIRST 1 NOMINA_ID
                , FREPAG_ID
                , FECHA
                , FECHA_PAGO
                , FECHA_INICIAL
                , FECHA_FINAL
                , APLICADO
                , CONTABILIZADO
                FROM NOMINAS
                ORDER BY NOMINA_ID DESC
        """)

        nomina = cur.fetchall()
        con.close()
        return nomina

    def _get_payroll_exceptions(self, payroll_id):
        con = self._get_connection()
        cur = con.cursor()

        cur.execute("""
            SELECT
                EED.EXCEP_EMP_ID,
                EED.EXCEP_EMP_DET_ID,
                CON.NOMBRE,
                EMP.NUMERO
            FROM EXCEP_EMPLEADOS_DET EED
            JOIN EXCEP_EMPLEADOS EEM ON EEM.EXCEP_EMP_ID = EED.EXCEP_EMP_ID
            JOIN CONCEPTOS_NO CON ON CON.CONCEPTO_NO_ID = EED.CONCEPTO_NO_ID
            JOIN EMPLEADOS EMP ON EMP.EMPLEADO_ID = EEM.EMPLEADO_ID
            WHERE EEM.NOMINA_ID = %s
        """ % (int(payroll_id)))

        excepciones = cur.fetchall()
        con.close()
        return excepciones

    def _get_attendances_in_period(self, employee_id=None):
        attendances = self.env['hr.attendance'].search([
            ('date', '>=', self.date_start),
            ('date', '<=', self.date_end),
            ('employee_id', '=', employee_id)
        ], order="check_in asc")
        return attendances

    def _get_leaves_in_period(self, time_type=None, employee_id=None, only_for_paid=False):
        domain = [
            ('holiday_status_id.time_type', '=', time_type),
            ('employee_id', '=', employee_id)]

        if only_for_paid:
            domain = domain + [('for_payroll', '=', True)]

        leaves_starting = self.env['hr.leave'].sudo().search(domain + [
            ('request_date_from', '>=', self.date_start),
            ('request_date_from', '<=', self.date_end)
        ]).ids

        leaves_ending = self.env['hr.leave'].sudo().search(domain + [
            ('request_date_to', '>=', self.date_start),
            ('request_date_to', '<=', self.date_end)
        ]).ids

        unique_ids = list(set(leaves_starting + leaves_ending))

        leaves = self.env['hr.leave'].sudo().browse(unique_ids)
        return leaves

    @api.multi
    def open_prepayroll_microsip(self):
        last_payroll = self._get_last_payroll_id_from_ms()
        if last_payroll[0][6] != 'N':
            raise UserError(_("Cannot find an opened payroll \
                in Microsip"))

        payroll_excep = self._get_payroll_exceptions(last_payroll[0][0])
        if payroll_excep:
            raise UserError(_("The last opened payroll \
                in Microsip has already exceptions"))

        atendances = self.env['hr.attendance'].search([
            ('check_in', '>=', self.date_start),
            ('check_out', '<=', self.date_end)])

        employees = atendances.mapped('employee_id').mapped('id_microsip')

        self._set_payroll_exceptions(employees, last_payroll[0][0])

        return {'type': 'ir.actions.act_window_close'}
