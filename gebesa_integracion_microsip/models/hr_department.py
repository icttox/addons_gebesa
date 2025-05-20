# Copyright 2022, Marco Esquivel
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api
from odoo.exceptions import ValidationError
import fdb


class HrDepartment(models.Model):
    _inherit = 'hr.department'

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
        # import ipdb; ipdb.set_trace()
        con = self._get_connection()
        cur = con.cursor()

        cur.execute("""
            SELECT
                DEPTO_NO_ID,
                NOMBRE,
                SUBSTRING(NOMBRE FROM 1 FOR 6)
            FROM DEPTOS_NO
        """)
        result = cur.fetchall()

        for depa_micro in result:
            department = self.search([('id_microsip', '=', depa_micro[0])])
            if department:
                department.write({
                    'name': depa_micro[1]
                })
            else:
                department.create({
                    'id_microsip': depa_micro[0],
                    'name': depa_micro[1],
                    'code': depa_micro[2],
                    'company_id': self.env.user.company_id.id
                })
        con.close()
