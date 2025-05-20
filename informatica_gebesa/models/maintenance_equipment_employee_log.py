# -*- coding: utf-8 -*-
# © <2018> <Aldo Nerio>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class MaintenanceEquipmentEmployeeLog(models.Model):
    _name = 'maintenance.equipment.employee.log'
    _description = 'descripcion pendiente'

    equipment_id = fields.Many2one(
        'maintenance.equipment',
        string='Equipment',
    )
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
    )
    date = fields.Date(
        string=('Fecha Asignacion'),
        copy=False)
    reason_reassignment = fields.Text(
        string='Fecha de Re-Asignacion',
    )
