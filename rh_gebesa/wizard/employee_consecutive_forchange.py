# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import re
from odoo import api, fields, models
from odoo.exceptions import UserError


class EmployeeConsecutiveForchange(models.TransientModel):
    _name = 'employee.consecutive.forchange.wizard'
    _description = 'descripcion pendiente'

    consecutivo = fields.Char(
        string='New Employee Number',
    )

    @api.multi
    def change_uom_id(self):
        res_id = self._context.get('active_ids')
        regex = re.compile("[A-Z]{3}-[0-9]{6}$")
        if not regex.match(self.consecutivo):
            raise UserError("Formato de numero no valido")
        for res in res_id:
            self.env.cr.execute("""UPDATE hr_employee SET consecutive_id = %s
                                WHERE id = %s """, (self.consecutivo, res))
            employee = self.env['hr.employee'].search([('id', '=', res)])
            employee.message_post(body=u"""
                <ul>
                    <li>
                        <b>Employee Number
                            <b>: %s → %s</b>
                        </b>
                    </li>
                </ul>""" % (employee.consecutive_id, self.consecutivo),
                subject="Cambios en Campos")
