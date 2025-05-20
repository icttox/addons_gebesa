# -*- coding: utf-8 -*-
# © <2017> <Aldo Nerio>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import fdb


class PayrollImportMicrosip(models.TransientModel):
    _name = 'payroll.import.microsip'
    _description = 'descripcion pendiente'

    journal_id = fields.Many2one(
        'account.journal',
        string='Journal',
    )
    date_start = fields.Date(
        string='Date start'
    )
    date_end = fields.Date(
        string='Date end'
    )

    def _set_messaje_error(self, move_id, error, data):
        message_body = u"<b>%s:</b><p>, Cuenta: %s, Analitica: %s, Concepto: %s, Montos: %s</p>"
        move_id.message_post(body=message_body % (
            error, str(data[1]), data[5].encode('ascii', 'ignore').decode(),
            data[0].encode('ascii', 'ignore').decode() + ' - ' + data[
                2].encode('ascii', 'ignore').decode(),
            data[3]) + ' | ' + str(data[4]))

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

    def _get_payroll(self):
        con = self._get_connection()
        cur = con.cursor()

        date_start = self.date_start.strftime("%d.%m.%Y")
        date_end = self.date_end.strftime("%d.%m.%Y")

        cur.execute("""
            SELECT
                N.NOMINA_ID,
                N.FECHA,
                N.TIPO_NOM,
                FP.NOMBRE AS FRECUENCIA
            FROM NOMINAS AS N
            LEFT JOIN FRECUENCIAS_PAGO AS FP ON N.FREPAG_ID = FP.FREPAG_ID
            WHERE N.FECHA >= '%s' AND N.FECHA <= '%s'
            """ % (date_start, date_end))

        payrolls = cur.fetchall()
        con.close()

        return payrolls

    def _get_payroll_lines(self, payroll_id):
        con = self._get_connection()
        cur = con.cursor()

        cur.execute("""
            SELECT
                CN.NOMBRE,
                COALESCE (CN.CUENTA_CONTABLE,CUN.CUENTA_CONTABLE, 'NO TIENE CUENTA') AS ACCOUNT_CODE,
                COALESCE (CN.CUENTA_CONTABLE,CUN.CUENTA_CONTABLE, 'NO TIENE CUENTA')|| ' - ' || DN.NOMBRE AS DESCRIPTION,
                SUM(
                    CASE
                    WHEN CN.NATURALEZA = 'P' THEN PND.IMPORTE
                    ELSE 0.0 END
                ) AS DEBIT,
                SUM(
                    CASE
                    WHEN CN.NATURALEZA = 'R'THEN PND.IMPORTE
                    ELSE 0.0 END
                ) AS CREDIT,
                DN.NOMBRE AS ANALYTIC,
                CN.CLAVE
            FROM NOMINAS AS N
            LEFT JOIN FRECUENCIAS_PAGO AS FP ON N.FREPAG_ID = FP.FREPAG_ID
            LEFT JOIN PAGOS_NOMINA AS PN ON N.NOMINA_ID = PN.NOMINA_ID
            LEFT JOIN EMPLEADOS AS E ON PN.EMPLEADO_ID = E.EMPLEADO_ID
            LEFT JOIN PUESTOS_NO AS PUN ON E.PUESTO_NO_ID = PUN.PUESTO_NO_ID
            LEFT JOIN DEPTOS_NO AS DN ON E.DEPTO_NO_ID = DN.DEPTO_NO_ID
            LEFT JOIN PAGOS_NOMINA_DET AS PND ON PN.PAGO_NOMINA_ID = PND.PAGO_NOMINA_ID
            LEFT JOIN CONCEPTOS_NO AS CN ON PND.CONCEPTO_NO_ID = CN.CONCEPTO_NO_ID
            LEFT JOIN CUENTAS_NO AS CUN ON CN.CONCEPTO_NO_ID = CUN.CONCEPTO_NO_ID AND DN.DEPTO_NO_ID = CUN.DEPTO_NO_ID
            LEFT JOIN CUENTAS_CO AS CC ON COALESCE (CUN.CUENTA_CONTABLE, CN.CUENTA_CONTABLE) = CC.CUENTA_PT
            LEFT JOIN CUENTAS_CO AS CC2 ON CC.CUENTA_PADRE_ID = CC2.CUENTA_ID
            WHERE N.NOMINA_ID = %s AND CN.NOMBRE IS NOT NULL
            GROUP BY CN.NOMBRE,CN.CLAVE,ACCOUNT_CODE, DESCRIPTION, ANALYTIC
            ORDER BY ACCOUNT_CODE
        """ % (int(payroll_id)))

        lines = cur.fetchall()
        con.close()
        return lines

    def _get_debit_credit(self, perception, retention):
        debit = credit = 0.0

        if perception > 0:
            debit = perception
        elif perception < 0:
            credit = abs(perception)

        if retention > 0:
            credit = retention
        elif retention < 0:
            debit = abs(retention)

        return debit, credit

    @api.multi
    def import_payroll_microsip(self):
        move_ids = []

        for pay in self._get_payroll():
            ref = pay[3] + ' ' + pay[2] + ' ' + str(pay[1])
            move_id = self.env['account.move'].search([('ref', '=', ref)])

            if move_id:
                continue

            move_id = self.env['account.move'].create({
                'journal_id': self.journal_id.id,
                'date': pay[1],
                'ref': ref,
                'company_id': self.env.user.company_id.id
            })
            move_ids.append(move_id.id)

            for line in self._get_payroll_lines(pay[0]):

                analytic_id = self.env['account.analytic.account'].search(
                    [('name', '=', line[5])])
                if not analytic_id:
                    self._set_messaje_error(
                        move_id,
                        "Una línea de la nomina no se ha importado. No se encontro la cuenta analitica:",
                        line
                    )
                    continue

                debit, credit = self._get_debit_credit(
                    float(line[3]), float(line[4]))

                account_id = self.env['account.account'].search(
                    [('code', '=', line[1])])
                if not account_id:
                    salary_rule = self.env['hr.salary.rule'].search([
                        ('code', '=', line[6])])
                    if salary_rule:
                        if debit > credit:
                            account_id = salary_rule.account_debit
                        else:
                            account_id = salary_rule.account_credit

                if not account_id:
                    self._set_messaje_error(
                        move_id,
                        "Una línea de la nomina no se ha importado. No se encontro la cuenta contable:",
                        line
                    )
                    continue

                line_name = (line[0] + ' - ' + line[2]).replace(
                    'NO TIENE CUENTA', account_id.code)

                self.env['account.move.line'].with_context(
                    {'check_move_validity': False}).create({
                        'move_id': move_id.id,
                        'journal_id': self.journal_id.id,
                        'date': pay[1],
                        'debit': debit,
                        'credit': credit,
                        'name': line_name,
                        'account_id': account_id.id,
                        'analytic_account_id': analytic_id.id,
                    })

        if move_ids:
            return {
                'name': _('Account Entries'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'account.move',
                'view_id': False,
                'domain': [('id', 'in', move_ids)],
            }
        return {'type': 'ir.actions.act_window_close'}
