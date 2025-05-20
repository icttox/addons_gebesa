# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, api, models


class MaintenanceEquipmentEmployeeLogWz(models.TransientModel):
    _name = 'maintenance.equipment.employee.log.wz'
    _description = 'descripcion pendiente'

    employee_id = fields.Many2one(
        'hr.employee',
        string='Nombre',
    )
    date = fields.Date(
        string=('Fecha Asignacion'),
        copy=False,
        required=True)

    reason_reassignment = fields.Text(
        string='Razon de Re-Asignacion',
        required=True)

    @api.multi
    def hr_equipment_employee_log_wz_m(self):

        hr_equipment_obj = self.env['maintenance.equipment']
        hr_equipment_employee_log_obj = self.env['maintenance.equipment.employee.log']
        active_ids = self._context.get('active_ids', []) or []
        sequipment = hr_equipment_obj.browse(active_ids)
        for equipo in sequipment:
            equipo.write(
                {'employee_id': self.employee_id.id,
                    'assign_date': self.date})
            hr_equipment_employee_log_obj.create(
                {'equipment_id': equipo.id,
                 'employee_id': self.employee_id.id,
                 'date': self.date,
                 'reason_reassignment': self.reason_reassignment})
