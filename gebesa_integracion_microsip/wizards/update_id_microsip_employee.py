# Copyright 2022, Samuel Barron
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import logging
from odoo import _, models
from odoo.exceptions import ValidationError
import fdb

_logger = logging.getLogger(__name__)


class UpdateIdMicrosipEmployee(models.TransientModel):
    _name = 'update.id.microsip.employee'
    _description = 'Import id microsip from firebird'

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

    def get_employee_microsip(self):
        con = self._get_connection()
        cur = con.cursor()
        cur.execute("""
            SELECT MAX(EMPLEADO_ID), REPLACE(RFC,'-','')
            FROM EMPLEADOS
            WHERE RFC IS NOT NULL
                AND ESTATUS = 'A'
            GROUP BY REPLACE(RFC,'-','')""")
        result = cur.fetchall()
        con.close()
        return result

    def update_id_microsip(self):
        empleados = self.get_employee_microsip()

        for empleado in empleados:
            employee = self.env['hr.employee'].search([
                ('rfc', '=', empleado[1])], order='id', limit=1)
            if employee and employee.id_microsip != empleado[0]:
                _logger.error(employee.name)
                employee.write({'id_microsip': empleado[0]})
