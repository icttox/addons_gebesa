# Copyright 2022, Samuel Barron
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, models
from datetime import timedelta


class ReportAbsenceReport(models.AbstractModel):
    _name = 'report.to_attendance_device.report_absence_report'
    _description = 'Absence Report'

    @api.multi
    def _get_report_values(self, docids, data=None):
        self.model = 'attendance.reports.wizard'
        doc = self.env[self.model].browse(docids)
        absence = {}
        employees = {}

        dates = []
        delta = doc.end_date - doc.start_date
        for dat in range(delta.days + 1):
            dates += [doc.start_date + timedelta(days=dat)]

        domain_department = doc.get_domain_department()
        domain_employee = doc.get_domain_employee()
        departments = self.env['hr.department'].search(domain_department)

        domain = [('date', '>=', doc.start_date), ('date', '<=', doc.end_date)]
        for dep in departments:
            absence[dep.id] = {}
            employees = self.env['hr.employee'].search(
                domain_employee + [('department_id', '=', dep.id)],
                order="consecutive_id asc")

            for emp in employees:
                attendance = self.env['hr.attendance'].search(
                    domain + [('employee_id', '=', emp.id)], order="check_in asc")
                for dat in dates:
                    if str(dat.weekday()) not in emp.resource_calendar_id.attendance_ids.mapped('dayofweek'):
                        continue
                    att = attendance.filtered(lambda attendance: attendance.date == dat)
                    if not att:
                        leave = self.env['hr.leave'].search([
                            ('employee_id', '=', emp.id),
                            ('request_date_from', '<=', dat),
                            ('request_date_to', '>=', dat),
                            ('state', 'not in', ('cancel', 'refuse'))])

                        if not leave or leave.holiday_status_id.time_type not in ('vacation', 'inhability'):
                            if emp.consecutive_id not in absence[dep.id]:
                                absence[dep.id][emp.consecutive_id] = {
                                    'emp': emp
                                }
                            leave_type = ''
                            if leave:
                                leave_type = " - ".join(leave.mapped('holiday_status_id').mapped('code'))
                            absence[dep.id][emp.consecutive_id][dat] = leave_type

            if len(absence[dep.id]) == 0:
                del absence[dep.id]

        docargs = {
            'doc_ids': docids,
            'doc_model': self.model,
            'docs': doc,
            'absence': absence,
            'departments': departments,
            'dates': dates,
        }
        return docargs
