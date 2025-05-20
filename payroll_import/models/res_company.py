# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, models, fields
from odoo.exceptions import ValidationError
import fdb


class ResCompany(models.Model):
    _inherit = 'res.company'

    db_microsip = fields.Char(
        string='DB Microsip',
    )
    user_microsip = fields.Char(
        string='User Microsip',
    )
    pass_microsip = fields.Char(
        string='Password Microsip',
    )
    host_microsip = fields.Char(
        string='Host Microsip',
    )
    port_microsip = fields.Integer(
        string='Port Microsip',
    )

    def _get_microsip_connection(self):
        if not self.db_microsip:
            raise ValidationError(_("Please specify a microsip database \
                for the company"))
        if not self.user_microsip:
            raise ValidationError(_("Please specify a microsip user \
                for the company"))
        if not self.pass_microsip:
            raise ValidationError(_("Please specify a microsip password \
                for the company"))
        if not self.host_microsip:
            raise ValidationError(_("Please specify a microsip host \
                for the company"))
        if not self.port_microsip:
            raise ValidationError(_("Please specify a microsip port \
                for the company"))

        con = fdb.connect(
            host=self.host_microsip, database=self.db_microsip,
            port=self.port_microsip, user=self.user_microsip,
            password=self.pass_microsip, charset='WIN1251')

        return con
