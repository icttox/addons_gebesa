# Copyright 2022, Marco Esquivel
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api
from odoo.exceptions import ValidationError
import fdb


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    id_microsip = fields.Integer(
        string='Microsip id',
    )

    def _get_connection(self):
        db_m = self.env.user.company_id.db_microsip
        user = self.env.user.company_id.user_microsip
        passw = self.env.user.company_id.pass_microsip
        host = self.env.user.company_id.host_microsip
        port = self.env.user.company_id.port_microsip

        if not db_m:
            raise ValidationError("Please specify a microsip database \
                for the company")
        if not user:
            raise ValidationError("Please specify a microsip user \
                for the company")
        if not passw:
            raise ValidationError("Please specify a microsip password \
                for the company")
        if not host:
            raise ValidationError("Please specify a microsip host \
                for the company")
        if not port:
            raise ValidationError("Please specify a microsip port \
                for the company")

        try:
            con = fdb.connect(
                host=host, database=db_m, port=port,
                user=user, password=passw, charset='WIN1251')
        except fdb.DatabaseError:
            raise ValidationError("Failed to establish connection to \
                the database")

        return con

    @api.multi
    def get_data_from_microsip(self):
        con = self._get_connection()
        cur = con.cursor()

        for employee in self:
            if not employee.company_id:
                continue
            if not employee.id_microsip or employee.id_microsip < 1:
                continue

            cur.execute("""
                SELECT
                    REPLACE(REPLACE(E.RFC,'-',''),' ',''),
                    E.REG_IMSS,
                    E.UNIDAD_MEDICA,
                    E.CURP,
                    TRIM(CASE E.SEXO
                        WHEN 'M' THEN 'male'
                        WHEN 'F' THEN 'female'
                        ELSE 'other' END) AS "SEXO",
                    E.DEPTO_NO_ID,
                    E.PUESTO_NO_ID,
                    CE_DE.CUOTA AS "DESPENSA",
                    'weekly',
                    CE_PP.CUOTA AS "PUNTUALIDAD",
                    CE_PA.CUOTA AS "ASISTENCIA",
                    E.SALARIO_DIARIO,
                    E.SALARIO_HORA
                FROM EMPLEADOS AS E
                LEFT JOIN CONCEPTOS_EMP AS CE_PP ON E.EMPLEADO_ID = CE_PP.EMPLEADO_ID
                    AND CE_PP.CONCEPTO_NO_ID IN (
                        SELECT CONCEPTO_NO_ID FROM CONCEPTOS_NO WHERE CLAVE IN ('1PP','PPF'))
                LEFT JOIN CONCEPTOS_EMP AS CE_PA ON E.EMPLEADO_ID = CE_PA.EMPLEADO_ID
                    AND CE_PA.CONCEPTO_NO_ID IN (
                        SELECT CONCEPTO_NO_ID FROM CONCEPTOS_NO WHERE CLAVE IN ('1IN','PAF'))
                LEFT JOIN CONCEPTOS_EMP AS CE_DE ON E.EMPLEADO_ID = CE_DE.EMPLEADO_ID
                    AND CE_DE.CONCEPTO_NO_ID IN (
                        SELECT CONCEPTO_NO_ID FROM CONCEPTOS_NO WHERE CLAVE IN ('2DP', 'DESP'))
                WHERE E.EMPLEADO_ID = ?""", (employee.id_microsip,))
            result = cur.fetchall()

            if not result:
                raise ValidationError("No se encontro el empleado %s(%s) en \
                    la base de datos de microsip" % (employee.name, employee.id_microsip))
            result = result[0]

            department = self.env['hr.department'].search([('id_microsip', '=', result[5])])
            job = self.env['hr.job'].search([('id_microsip', '=', result[6])])

            employee.write({
                'rfc': result[0],
                'imss': result[1],
                'umf': result[2],
                'curp': result[3],
                'gender': result[4],
                'department_id': department.id,
                'job_id': job.id,
            })
            wage = round(float((
                ((result[11] or 0) * 7) + (result[9] or 0) + (
                    result[10] or 0) + (result[7] or 0)) / 7) * 30.42, 2)
            employee.contract_id.write({
                'department_id': department.id,
                'job_id': job.id,
                'wage': wage,
                'schedule_pay': result[8],
                'premio_puntualidad': result[9],
                'premio_asistencia': result[10],
                'salario_diario': result[11],
                'salario_hora': result[12],
            })

        con.close()

    def _check_employee_microsip(self, cur):
        cur.execute("""
            SELECT EMPLEADO_ID
            FROM EMPLEADOS
            WHERE NUMERO = ?
                OR RFC = ?
                OR CURP = ?
            """, (int(self.identification_id), self.rfc, self.curp))
        return cur.fetchall()

    @api.multi
    def send_employee_microsip(self):
        # import ipdb; ipdb.set_trace()
        con = self._get_connection()
        cur = con.cursor()

        marital_state = {
            'single': 'S',
            'married': 'C',
            'cohabitant': 'U',
            'widower': 'V',
            'divorced': 'D'
        }

        # employees = self.filtered(lambda emp: emp.id)
        for emp in self:
            in_microsip = emp._check_employee_microsip(cur)
            if in_microsip:
                con.close()
                raise ValidationError("El empleado ya se encuentra em microsip")
            if not emp.entry_date_vacation:
                raise ValidationError("Por favor asigne una fecha de entrada para días festivos")
            if not emp.gender:
                raise ValidationError("Por favor asigna un género")
            if not emp.marital:
                raise ValidationError("Por favor asigne un estado civil")
            if not emp.job_id.id_microsip:
                raise ValidationError("Por favor asigne un titulo de trabajo existente")
            if not emp.department_id.id_microsip:
                raise ValidationError("Por favor asigne un departamento existente")

            nombres = emp.name.split(' ')
            ap_materno = ''.join(nombres[-1])
            ap_paterno = ''.join(nombres[-2])
            nombre = ' '.join(nombres[:-2])

            date_vacation = emp.entry_date_vacation.strftime("%d.%m.%Y")
            date_birthday = emp.birthday.strftime("%d.%m.%Y")

            sindicalizado = 'S'
            if not emp.sindicalizado:
                sindicalizado = 'N'

            status_active = 'A'
            if not emp.active:
                status_active = 'B'

            ptu = 'S'
            if not emp.contract_id.ptu:
                ptu = 'N'

            imss = 'S'
            if not emp.contract_id.imss:
                imss = 'N'

            cas = 'S'
            if not emp.contract_id.cas:
                cas = 'N'

            pensionado = 'S'
            if not emp.contract_id.pensionado:
                pensionado = 'N'

            deshab_imptos = 'S'
            if not emp.contract_id.deshab_imptos:
                deshab_imptos = 'N'

            calc_isr_anual = 'S'
            if not emp.contract_id.calc_isr_anual:
                calc_isr_anual = 'N'

            gender_state = 'M'
            if emp.gender == 'female':
                gender_state = 'F'

            cur.execute("""
                SELECT MAX(EMPLEADO_ID) + 1
                FROM EMPLEADOS
            """)
            id_empleado = cur.fetchall()[0][0]

            cur.execute("""
                INSERT INTO EMPLEADOS(
                    EMPLEADO_ID, NUMERO, NOMBRE_COMPLETO, APELLIDO_PATERNO,
                    APELLIDO_MATERNO, NOMBRES, REGIMEN, PUESTO_NO_ID,
                    DEPTO_NO_ID, FREPAG_ID, REG_PATRONAL_ID, TURNO_ID, ES_JEFE, JEFE_INMEDIATO_ID,
                    FORMA_PAGO, CONTRATO, DIAS_HRS_JSR, HORARIO,
                    TURNO, JORNADA, REGIMEN_FISCAL, CONTRATO_SAT,
                    JORNADA_SAT, ES_SINDICALIZADO, FECHA_INGRESO, ESTATUS,
                    ZONA_SALMIN, TABLA_ANTIG_ID, TIPO_SALARIO, PCTJE_INTEG,
                    SALARIO_DIARIO, SALARIO_HORA, SALARIO_INTEG, ES_DIR_ADMR_GTE_GRAL, PTU,
                    IMSS, CAS, PENSIONADO, TIPO_PENSION,
                    DESHAB_IMPTOS, CALC_ISR_ANUAL, CALLE, NOMBRE_CALLE,
                    NUM_EXTERIOR, NUM_INTERIOR, COLONIA, POBLACION,
                    REFERENCIA, CIUDAD_ID, CODIGO_POSTAL, TELEFONO1,
                    TELEFONO2, EMAIL, SEXO, FECHA_NACIMIENTO,
                    CIUDAD_NACIMIENTO_ID, ESTADO_CIVIL, NUM_HIJOS, NOMBRE_PADRE,
                    NOMBRE_MADRE, RFC, CURP, REG_IMSS,
                    OTRO_REG, UNIDAD_MEDICA, GRUPO_PAGO_ELECT_ID, TIPO_CTABAN_PAGO_ELECT,
                    NUM_CTABAN_PAGO_ELECT, USUARIO_CREADOR, FECHA_HORA_CREACION, USUARIO_AUT_CREACION,
                    USUARIO_ULT_MODIF, FECHA_HORA_ULT_MODIF, USUARIO_AUT_MODIF)
                VALUES (
                    ?, ?, ?, ?,
                    ?, ?, 'S', ?,
                    ?, ?, 274, NULL, FALSE, NULL,
                    'E', 'P', 0.0, NULL,
                    'M', ?, ?, ?,
                    ?, ?, ?, ?,
                    ?, 142, '0', ?,
                    ?, ?, ?, FALSE, ?,
                    ?, ?, ?, NULL,
                    ?, ?, ?, ?,
                    ?, ?, ?, NULL,
                    NULL, 272, ?, ?,
                    ?, ?, ?, ?,
                    272, ?, ?, ?,
                    ?, ?, ?, ?,
                    NULL, ?, 614, 'D',
                    NULL, ?, ?, NULL,
                    'ODOOBOT', NULL, NULL)
            """, (
                id_empleado, int(emp.identification_id), emp.name, ap_paterno,
                ap_materno, nombre, emp.job_id.id_microsip,
                emp.department_id.id_microsip, emp.contract_id.struct_id.id_microsip,

                emp.resource_calendar_id.hours_per_day, int(emp.contract_id.regimen), int(emp.contract_id.contrato),
                int(emp.contract_id.jornada), sindicalizado, date_vacation, status_active,
                emp.contract_id.zona_salmin, emp.contract_id.pctjre_integ,
                emp.contract_id.salario_diario, emp.contract_id.salario_hora, emp.contract_id.salario_integ, ptu,
                imss, cas, pensionado,
                deshab_imptos, calc_isr_anual, emp.address_home_id.street, emp.address_home_id.street,
                emp.address_home_id.street_number, emp.address_home_id.street_number2, emp.address_home_id.l10n_mx_edi_colony,
                emp.address_home_id.zip, emp.address_home_id.phone,
                emp.address_home_id.mobile, emp.work_email, gender_state, date_birthday,
                marital_state[emp.marital], emp.children, emp.father,
                emp.mother, emp.rfc, emp.curp, emp.imss,
                emp.umf,
                str(self.env.user.name)[:31], fields.Datetime.now()

            ))
            con.commit()
        con.close()
