# Copyright 2022, Marco Esquivel
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api
from odoo.exceptions import ValidationError
import fdb


class HrJob(models.Model):
    _inherit = 'hr.job'

    id_microsip = fields.Integer(
        string='Microsip id',
    )
    active = fields.Boolean(
        string='Active',
        default=True,
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
                PUESTO_NO_ID,
                NOMBRE
            FROM PUESTOS_NO
        """)
        result = cur.fetchall()

        for job_micro in result:
            job = self.search([('id_microsip', '=', job_micro[0])])
            if job:
                job.write({
                    'name': job_micro[1]
                })
            else:
                job.create({
                    'id_microsip': job_micro[0],
                    'name': job_micro[1],
                    'company_id': self.env.user.company_id.id
                })
        con.close()
