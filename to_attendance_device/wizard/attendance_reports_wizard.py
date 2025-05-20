# Copyright 2022, Samuel Barron
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class AttendanceReportsWizard(models.TransientModel):
    _name = 'attendance.reports.wizard'
    _description = 'Wizard para generar los reportes de asistencia'

    department_ids = fields.Many2many(
        'hr.department',
        string='Departments',
    )
    employee_ids = fields.Many2many(
        'hr.employee',
        string='Employees',
    )
    start_date = fields.Date(
        string='Start date'
    )
    end_date = fields.Date(
        string='End date'
    )

    def print_absence_report(self):
        return self.env.ref('to_attendance_device.absence_report').report_action(self)

    def print_time_card(self):
        return self.env.ref('to_attendance_device.time_card').report_action(self)

    def print_attendance_summary_report(self):
        return self.env.ref('to_attendance_device.attendance_summary_report').report_action(self)

    def get_domain_department(self):
        domain = []
        if self.employee_ids:
            domain += [('id', 'in', self.employee_ids.mapped('department_id').mapped('id'))]
        elif self.department_ids:
            domain += [('id', 'in', self.department_ids.ids)]
        return domain

    def get_domain_employee(self):
        domain = [('rfc', '!=', 'XAXX010101000')]
        if self.employee_ids:
            domain += [('id', 'in', self.employee_ids.ids)]
        return domain
