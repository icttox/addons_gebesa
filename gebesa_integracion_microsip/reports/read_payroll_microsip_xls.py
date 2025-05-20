# Copyright 2023, Samuel Barron
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models
from odoo.tools.translate import _
from odoo.exceptions import ValidationError
import fdb
from itertools import product
import string


def copy_format(book, fmt):
    properties = [f[4:] for f in dir(fmt) if f[0:4] == 'set_']
    dft_fmt = book.add_format()
    res = book.add_format(
        {k: v for k, v in fmt.__dict__.items() if k in properties and dft_fmt.__dict__[k] != v})
    return res


class ReadPayrollMicrosipXlsx(models.AbstractModel):
    _name = 'report.gebesa_integracion_microsip.read_payroll_microsip_xlsx'
    _inherit = 'report.report_xlsx.abstract'

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

    def get_payroll_concepts(self, payroll, cur):
        cur.execute("""
            SELECT
                CN.CONCEPTO_NO_ID,
                CN.NOMBRE,
                CN.CLAVE,
                CN.NATURALEZA
            FROM PAGOS_NOMINA AS PN
            LEFT JOIN PAGOS_NOMINA_DET AS PND ON PN.PAGO_NOMINA_ID = PND.PAGO_NOMINA_ID
            LEFT JOIN CONCEPTOS_NO AS CN ON PND.CONCEPTO_NO_ID = CN.CONCEPTO_NO_ID
            WHERE PN.NOMINA_ID = ?
            GROUP BY CN.CONCEPTO_NO_ID, CN.NOMBRE, CN.CLAVE, CN.NATURALEZA
            ORDER BY CN.NATURALEZA,CN.CLAVE
        """, (str(payroll),))
        return cur.fetchall()

    def get_pago_nomina(self, payroll, cur):
        cur.execute("""
            SELECT
                E.EMPLEADO_ID AS "EMPLEADO_ID",
                E.NUMERO AS "EMPLEADO",
                SUBSTRING(DN.NOMBRE FROM 1 FOR (POSITION(' ' IN DN.NOMBRE) - 1)) AS "CCOSTO",
                SUBSTRING(DN.NOMBRE FROM (POSITION(' ' IN DN.NOMBRE) + 1)) AS "DPTO",
                E.NUMERO AS "NOMBRE",
                PN.DIAS_TRAB AS "DIAST",
                PN.FALTAS_DEC,
                PN.DIAS_INCAP,
                E.SALARIO_DIARIO "SDIARIO",
                E.SALARIO_INTEG "SDI",
                PN.HORAS_TRAB AS "HORASTRAB",
                PN.HORAS_EXT_DEC AS "HORASEXT",
                PN.HORAS_EXT_DEC * ((E.SALARIO_DIARIO / 8) * 2) AS "PAGOS_NOMINA_HORAS_EXT",
                PN.TOTAL_PERCEP "PERCEP",
                PN.TOTAL_RETEN AS "DEDUC",
                PN.TOTAL_PERCEP - PN.TOTAL_RETEN AS "PAGO",
                PN.PAGO_NOMINA_ID
            FROM PAGOS_NOMINA AS PN
            LEFT JOIN EMPLEADOS AS E ON PN.EMPLEADO_ID = E.EMPLEADO_ID
            LEFT JOIN DEPTOS_NO AS DN ON E.DEPTO_NO_ID = DN.DEPTO_NO_ID
            WHERE PN.NOMINA_ID = ?
            ORDER BY DN.NOMBRE,E.NUMERO
            """, (str(payroll),))

        return cur.fetchall()

    def get_detalle_nomina(self, pago_nomina, empleado, cur):
        cur.execute("""
            SELECT
                PND.CONCEPTO_NO_ID,
                PND.IMPORTE
            FROM PAGOS_NOMINA_DET AS PND
            WHERE PND.PAGO_NOMINA_ID = ?
                AND PND.EMPLEADO_ID = ?
            """, (str(pago_nomina), str(empleado)))

        return cur.fetchall()

    def generate_xlsx_report(self, workbook, data, objects):
        con = self._get_connection()
        cur = con.cursor()

        workbook.set_properties({
            'comments': 'Created with Python and XlsxWriter from Odoo 12.0'})

        title_format = workbook.add_format({
            'border': 1,
            'bold': 1,
            'align': 'center',
            'valign': 'vcenter',
            'font_size': 10,
        })

        row_format = workbook.add_format({
            'border': 1,
            'font_size': 10,
        })

        columns = tuple(list(string.ascii_uppercase))
        columns = list(product(('',) + columns, columns))

        cur.execute("""
            SELECT
                N.NOMINA_ID,
                N.FECHA,
                N.TIPO_NOM
            FROM NOMINAS AS N
            WHERE N.FECHA >= ? AND N.FECHA <= ?
            """, (objects.date_start.strftime('%Y.%m.%d'),
                  objects.date_end.strftime('%Y.%m.%d')))
        payrolls = cur.fetchall()

        for payroll in payrolls:
            sheet = workbook.add_worksheet(_(
                'Payroll ') + payroll[1].strftime('%d-%m-%Y') + ' ' + payroll[2])
            sheet.set_column(0, 200, 13)
            row = 1

            sheet.write(''.join(columns[0]) + str(row), 'EMPLEADO', title_format)
            sheet.write(''.join(columns[1]) + str(row), 'CCOSTO', title_format)
            sheet.write(''.join(columns[2]) + str(row), 'DPTO', title_format)
            sheet.write(''.join(columns[3]) + str(row), 'NOMBRE', title_format)
            sheet.write(''.join(columns[4]) + str(row), 'DIAST', title_format)
            sheet.write(''.join(columns[5]) + str(row), 'FALTAS_DEC', title_format)
            sheet.write(''.join(columns[6]) + str(row), 'DIAS_INCAP', title_format)
            sheet.write(''.join(columns[7]) + str(row), 'SDIARIO', title_format)
            sheet.write(''.join(columns[8]) + str(row), 'SDI', title_format)
            sheet.write(''.join(columns[9]) + str(row), 'HORASTRAB', title_format)
            sheet.write(''.join(columns[10]) + str(row), 'HORASEXT', title_format)
            sheet.write(''.join(columns[11]) + str(row), 'PAGOS_NOMINA_HORAS_EXT', title_format)

            concepts = self.get_payroll_concepts(payroll[0], cur)

            dict_concept = {}
            next_col = 12
            nature = concepts[0][3]
            for concept in concepts:
                if nature != concept[3]:
                    sheet.write(
                        ''.join(columns[next_col]) + str(row),
                        'PERCEP', title_format)
                    dict_concept['PERCEP'] = ''.join(columns[next_col])
                    nature = concept[3]
                    next_col += 1

                sheet.write(
                    ''.join(columns[next_col]) + str(row),
                    concept[1] if concept[1] else concept[2],
                    title_format)
                dict_concept[concept[0]] = ''.join(columns[next_col])

                next_col += 1

            if 'PERCEP' not in dict_concept:
                sheet.write(
                    ''.join(columns[next_col]) + str(row),
                    'PERCEP', title_format)
                dict_concept['PERCEP'] = ''.join(columns[next_col])
                nature = concept[3]
                next_col += 1

            sheet.write(
                ''.join(columns[next_col]) + str(row),
                'DEDUC', title_format)
            dict_concept['DEDUC'] = ''.join(columns[next_col])
            next_col += 1
            sheet.write(
                ''.join(columns[next_col]) + str(row),
                'PAGO', title_format)
            dict_concept['PAGO'] = ''.join(columns[next_col])

            pagos_nom = self.get_pago_nomina(payroll[0], cur)

            row += 1
            for pago in pagos_nom:
                sheet.write(''.join(columns[0]) + str(row), pago[1], row_format)
                sheet.write(''.join(columns[1]) + str(row), pago[2], row_format)
                sheet.write(''.join(columns[2]) + str(row), pago[3], row_format)
                sheet.write(''.join(columns[3]) + str(row), pago[4], row_format)
                sheet.write(''.join(columns[4]) + str(row), pago[5], row_format)
                sheet.write(''.join(columns[5]) + str(row), pago[6], row_format)
                sheet.write(''.join(columns[6]) + str(row), pago[7], row_format)
                sheet.write(''.join(columns[7]) + str(row), pago[8], row_format)
                sheet.write(''.join(columns[8]) + str(row), pago[9], row_format)
                sheet.write(''.join(columns[9]) + str(row), pago[10], row_format)
                sheet.write(''.join(columns[10]) + str(row), pago[11], row_format)
                sheet.write(''.join(columns[11]) + str(row), pago[12], row_format)
                sheet.write(dict_concept['PERCEP'] + str(row), pago[13], row_format)
                sheet.write(dict_concept['DEDUC'] + str(row), pago[14], row_format)
                sheet.write(dict_concept['PAGO'] + str(row), pago[15], row_format)

                det_nom = self.get_detalle_nomina(pago[16], pago[0], cur)

                for detalle in det_nom:
                    sheet.write(dict_concept[detalle[0]] + str(row), detalle[1], row_format)

                row += 1

        con.commit()
        con.close()
