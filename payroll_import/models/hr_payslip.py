# Copyright 2022, Cesar Barron
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, fields, models
from odoo.exceptions import ValidationError
import fdb
from datetime import datetime, timedelta


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

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

    def _get_payslip_from_microsip(self):
        con = self._get_connection()
        cur = con.cursor()

        today = fields.Date.today()
        dt = datetime.strptime(str(today), '%Y-%m-%d')
        start = dt - timedelta(days=dt.weekday())
        end = start + timedelta(days=6)

        date_start = start.strftime("%d.%m.%Y")
        date_end = end.strftime("%d.%m.%Y")

        cur.execute("""
            SELECT
                NOM.NOMINA_ID
                , NOM.FREPAG_ID
                , NOM.FECHA AS NOM_FECHA
                , NOM.FECHA_PAGO AS NOM_FECHA_PAGO
                , NOM.FECHA_INICIAL AS NOM_FEC_INI
                , NOM.FECHA_FINAL AS NOM_FEC_FIN
                , NOM.TIPO_NOM
                , NOM.FECHA_HORA_CREACION AS USER_CREA_NOM
                , NOM.FECHA_HORA_CREACION AS HORA_CREA_NOM
                , NOM.USUARIO_ULT_MODIF AS USER_MOD_NOM
                , NOM.FECHA_HORA_ULT_MODIF AS FECH_MOD_NOM
                , PAG.PAGO_NOMINA_ID
                , PAG.EMPLEADO_ID
                , PAG.PUESTO_NO_ID
                , PAG.DEPTO_NO_ID
                , PAG.JORNADA
                , PAG.TIPO_SALARIO
                , PAG.SALARIO_INTEG
                , PAG.DIAS_TRAB
                , PAG.HORAS_TRAB
                , PAG.DIAS_VAC
                , PAG.DIAS_COT
                , PAG.FALTAS
                , PAG.FALTAS_DEC
                , PAG.DIAS_AUS_IMSS
                , PAG.DIAS_INCAP
                , PAG.HORAS_EXT
                , PAG.HORAS_EXT_DEC
                , PAG.HORAS_EXT_EXCED
                , PAG.IMPORTE_HORAS_EXT_EXCED
                , PAG.HORAS_ESP
                , PAG.HORAS_ESP_DEC
                , PAG.SBC_SMDF
                , PAG.SBC_EXCED
                , PAG.SBC_DIN
                , PAG.SBC_IV_CV
                , PAG.SBC_RETIRO
                , PAG.SBC_RIESGO
                , PAG.SBC_INFON
                , PAG.TOTAL_PERCEP
                , PAG.TOTAL_RETEN
                , PAG.TOTAL_PERCEP_ESPECIE
                , PAG.TOTAL_RETEN_DEDUC
                , PAG.TOTAL_PERCEP_GRAV
                , PAG.TOTAL_PERCEP_EXEN
                , PAG.TOTAL_PERCEP_NO_ACUM
                , PAG.TOTAL_TIPO_A
                , PAG.TOTAL_TIPO_B
                , PAG.TOTAL_TIPO_C
                , PAG.TOTAL_OTROS_PAGOS
                , PAG.TOTAL_OTROS_PAGOS_INFO
                , PAG.FECHA AS PAGO_FECHA
                , PAG.TIPO_NOM
                , PAG.FORMA_PAGO
                , PAG.TIPO_PAGO
                , PAG.APLICADO
                , PAG.ENVIADO
                , PAG.FORMA_EMITIDA
                , PAG.FECHA_HORA_ENVIO
                , PAG.EMAIL_ENVIO
                , PAG.CFDI_CERTIFICADO
                , PAG.CONTABILIZADO_BA
                , PAG.CUENTA_BAN_ID
                , PAG.USUARIO_CREADOR AS USER_CREA_PAG
                , PAG.FECHA_HORA_CREACION AS FEC_CREA_PAG
                , PAG.USUARIO_ULT_MODIF AS USER_MOD_PAG
                , PAG.FECHA_HORA_ULT_MODIF AS FEC_MOD_PAG
                , FEC.FREPAG_ID
                , FEC.NOMBRE AS FRECUENCIA
                , FEC.DIAS_PERIODO
                , FEC.DIAS_A_COT
                , FEC.TIPO_PAGO
                , FEC.HORAS_PERIODO
                , FEC.PERIODICIDAD_SAT
                , FEC.TIPO_PROCESO
                , FEC.SEPTIMO_DIA
                , FEC.DIAS_NETOS
                , FEC.DESGL_SEPTIMO
                , FEC.INCAP_SEPTIMO
                , FEC.TARIFA_ISR
                , FEC.PERIODO_TABLA_ISR
                , FEC.HACER_AJUSTE
                , FEC.HACER_DEVOL
                , FEC.CALC_ISR
                , FEC.CALC_IMSS
                , FEC.CUENTA_PAGOS_EFECTIVO
                , FEC.CUENTA_PAGOS_TRANS
                , FEC.CUENTA_PAGOS_ESPECIE
                , FEC.TIPO_POLIZA
                , FEC.DESCRIPCION_POLIZA
                , FEC.ES_PREDET
                , FEC.USUARIO_CREADOR AS USER_CREA_FEC
                , FEC.FECHA_HORA_CREACION AS FEC_CREA_FEC
                , FEC.USUARIO_ULT_MODIF AS USER_MOD_FEC
                , FEC.FECHA_HORA_ULT_MODIF AS FECHA_MOD_FEC
                , DEP.DEPTO_NO_ID
                , DEP.NOMBRE AS DEPARTAMENTO
                , DEP.ES_PREDET
                , DEP.USUARIO_CREADOR AS USER_CREA_DEP
                , DEP.FECHA_HORA_CREACION AS FEC_CREA_DEP
                , DEP.USUARIO_ULT_MODIF AS USER_MOD_DEP
                , DEP.FECHA_HORA_ULT_MODIF AS FEC_MOD_DEP
                , PUE.PUESTO_NO_ID
                , PUE.NOMBRE AS PUESTO
                , PUE.SUELDO_DIARIO
                , PUE.SUELDO_DIARIO_MAX
                , PUE.ES_PREDET
                , PUE.USUARIO_CREADOR AS USER_CREA_PUE
                , PUE.FECHA_HORA_CREACION AS FEC_CREA_PUE
                , PUE.USUARIO_ULT_MODIF AS USER_MOD_PUE
                , PUE.FECHA_HORA_ULT_MODIF AS FEC_MOD_PUE
                , EMP.EMPLEADO_ID
                , EMP.NUMERO
                , EMP.NOMBRE_COMPLETO
                , EMP.APELLIDO_PATERNO
                , EMP.APELLIDO_MATERNO
                , EMP.NOMBRES
                , EMP.REGIMEN
                , EMP.PUESTO_NO_ID
                , EMP.DEPTO_NO_ID
                , EMP.FREPAG_ID
                , EMP.REG_PATRONAL_ID
                , EMP.TURNO_ID
                , EMP.FORMA_PAGO
                , EMP.CONTRATO
                , EMP.DIAS_HRS_JSR
                , EMP.HORARIO
                , EMP.TURNO
                , EMP.JORNADA
                , EMP.REGIMEN_FISCAL
                , EMP.CONTRATO_SAT
                , EMP.JORNADA_SAT
                , EMP.ES_SINDICALIZADO
                , EMP.FECHA_INGRESO
                , EMP.ESTATUS
                , EMP.ZONA_SALMIN
                , EMP.TABLA_ANTIG_ID
                , EMP.TIPO_SALARIO
                , EMP.PCTJE_INTEG
                , EMP.SALARIO_DIARIO
                , EMP.SALARIO_HORA
                , EMP.SALARIO_INTEG
                , EMP.PTU
                , EMP.IMSS
                , EMP.CAS
                , EMP.PENSIONADO
                , EMP.TIPO_PENSION
                , EMP.DESHAB_IMPTOS
                , EMP.CALC_ISR_ANUAL
                , EMP.CALLE
                , EMP.NOMBRE_CALLE
                , EMP.NUM_EXTERIOR
                , EMP.NUM_INTERIOR
                , EMP.COLONIA
                , EMP.POBLACION
                , EMP.REFERENCIA
                , EMP.CIUDAD_ID
                , EMP.CODIGO_POSTAL
                , EMP.TELEFONO1
                , EMP.TELEFONO2
                , EMP.EMAIL
                , EMP.SEXO
                , EMP.FECHA_NACIMIENTO
                , EMP.CIUDAD_NACIMIENTO_ID
                , EMP.ESTADO_CIVIL
                , EMP.NUM_HIJOS
                , EMP.NOMBRE_PADRE
                , EMP.NOMBRE_MADRE
                , EMP.RFC
                , EMP.CURP
                , EMP.REG_IMSS
                , EMP.OTRO_REG
                , EMP.UNIDAD_MEDICA
                , EMP.GRUPO_PAGO_ELECT_ID
                , EMP.TIPO_CTABAN_PAGO_ELECT
                , EMP.NUM_CTABAN_PAGO_ELECT

            FROM NOMINAS AS NOM
            JOIN FRECUENCIAS_PAGO AS FEC ON NOM.FREPAG_ID = FEC.FREPAG_ID
            JOIN PAGOS_NOMINA AS PAG ON PAG.NOMINA_ID = NOM.NOMINA_ID
            JOIN DEPTOS_NO DEP ON DEP.DEPTO_NO_ID = PAG.DEPTO_NO_ID
            JOIN PUESTOS_NO PUE ON PUE.PUESTO_NO_ID = PAG.PUESTO_NO_ID
            JOIN EMPLEADOS EMP ON EMP.EMPLEADO_ID = PAG.EMPLEADO_ID
            WHERE NOM.FECHA >= ? AND NOM.FECHA <= ? AND NOM.APLICADO = 'S'
            """, (date_start, date_end))

        payrolls = cur.fetchall()
        con.close()

        return payrolls

    def _get_payslip_lines_from_microsip(self, payroll_id):
        con = self._get_connection()
        cur = con.cursor()

        cur.execute("""
            SELECT DET.PAGO_NOMINA_DET_ID
            , DET.CONCEPTO_NO_ID
            , DET.CUOTA
            , DET.AHORRO_EMPRESA
            , DET.UNIDADES
            , DET.IMPORTE
            , DET.IMPORTE_GRAVABLE
            , DET.IMPORTE_EXENTO
            , DET.IMPORTE_AHORRO_EMPRESA
            , DET.ACUMULABLE
            , DET.EMPLEADO_ID
            , DET.FECHA
            , DET.APLICADO
            , CON.CONCEPTO_NO_ID
            , CON.NOMBRE
            , CON.NOMBRE_ABREV
            , CON.NATURALEZA
            , CON.TIPO
            , CON.CLAVE
            , CON.TIPO_SAT
            , CON.ASIGNAR_AUTOM_EMP
            , CON.ID_INTERNO
            , CON.FORMA_PAGO
            , CON.METODO_PAGO_ESPECIE
            , CON.EXENCION_ISR
            , CON.TIPO_PERCEP
            , CON.SALMIN_EXEN
            , CON.PERCEP_VAR_IMSS
            , CON.TIPO_INTEG_IMSS
            , CON.NO_INTEG_IMSS
            , CON.INTEG_PTU
            , CON.INTEG_IMPTO_ESTATAL
            , CON.PREV_SOCIAL
            , CON.TIPO_CALC
            , CON.PAGO_UNITARIO
            , CON.TABLA_NO_ID
            , CON.SIMBOLO_CUOTA
            , CON.CUOTA_DEFAULT
            , CON.AHORRO_EMPRESA_DEFAULT
            , CON.CUENTA_CONTABLE
            , CON.USUARIO_CREADOR
            , CON.FECHA_HORA_CREACION
            , CON.USUARIO_ULT_MODIF
            , CON.FECHA_HORA_ULT_MODIF
            FROM PAGOS_NOMINA_DET DET
            JOIN CONCEPTOS_NO CON ON CON.CONCEPTO_NO_ID = DET.CONCEPTO_NO_ID
            WHERE DET.PAGO_NOMINA_DET_ID = ? AND CON.NOMBRE IS NOT NULL
            --GROUP BY CON.NOMBRE,CON.CLAVE
            ORDER BY CON.NOMBRE
        """, (int(payroll_id)))

        lines = cur.fetchall()
        con.close()
        return lines

    def import_payslips_from_microsip(self):
        payslips = self._get_payslip_from_microsip()
        for pslip in payslips:
            payslip_data = self.prepare_payslip_data(pslip)
            self.env['hr.payslip'].create(payslip_data)

    def prepare_payslip_data(self, data=None):
        # find hr.employee EMPLEADO_ID
        # find hr.department DEPTO_NO_ID
        # find hr.job PUESTO_NO_ID
        # find hr.payslip.strucutre FREPAG_ID
        lines_raw = self._get_payslip_lines_from_microsip(self, data['PAGO_NOMINA_DET_ID'])
        lines = self.prepare_payslip_lines_data(lines_raw)
        return {

        }

    def prepare_payslip_lines_data(self, lines_raw=None):
        lines = []
        for lnrw in lines_raw:
            # find hr.salary.rule CONCEPTO_NO_ID
            lines.append()
        return lines
