# Copyright 2022, Samuel Barron
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, models
from datetime import timedelta


class ReportAttendanceSummary(models.AbstractModel):
    _name = 'report.to_attendance_device.report_attendance_summary'
    _description = 'Attendance Report'

    @api.multi
    def _get_report_values(self, docids, data=None):
        self.model = 'attendance.reports.wizard'
        doc = self.env[self.model].browse(docids)
        attendance = {}
        # employees = {}

        dates = []
        delta = doc.end_date - doc.start_date
        for dat in range(delta.days + 1):
            dates += [doc.start_date + timedelta(days=dat)]

        domain_department = doc.get_domain_department()
        domain_employee = doc.get_domain_employee()
        departments = self.env['hr.department'].search(domain_department)

        domain = [('date', '>=', doc.start_date), ('date', '<=', doc.end_date)]
        for dep in departments:
            attendance[dep.id] = {}
            employees = self.env['hr.employee'].search(
                domain_employee + [('department_id', '=', dep.id)],
                order="consecutive_id asc")
            for emp in employees:
                attendance[dep.id][emp.consecutive_id] = {
                    'emp': emp,
                    'att': {},
                    'lea': {},
                    'wt': {},
                    'ot': {},
                }
                att = self.env['hr.attendance'].search(
                    domain + [('employee_id', '=', emp.id)], order="check_in asc")
                for dat in dates:
                    current_att = att.filtered(
                        lambda attendance: attendance.date == dat)
                    attendance[dep.id][emp.consecutive_id]['att'][dat] = current_att

                    leave = self.env['hr.leave'].search([
                        ('employee_id', '=', emp.id),
                        ('request_date_from', '<=', dat),
                        ('request_date_to', '>=', dat),
                        ('state', 'not in', ('cancel', 'refuse'))])
                    leave_type = ''
                    if leave:
                        leave_type = " - ".join(leave.mapped('holiday_status_id').mapped('code'))
                    attendance[dep.id][emp.consecutive_id]['lea'][dat] = leave_type

                    attendance[dep.id][emp.consecutive_id]['wt'][dat] = ''
                    attendance[dep.id][emp.consecutive_id]['ot'][dat] = ''

                    time_total = time_work = overtime = False
                    time_lunch = timedelta(hours=emp.resource_calendar_id.break_time)
                    hours_average = timedelta(hours=emp.resource_calendar_id.hours_per_day)
                    if current_att.check_in and current_att.check_out:
                        time_total = current_att.check_out.replace(second=0) - current_att.check_in.replace(second=0)
                    if current_att.break_out and current_att.break_in:
                        time_lunch = current_att.break_in.replace(second=0) - current_att.break_out.replace(second=0)
                    if time_total:
                        time_work = time_total - time_lunch
                        if hours_average < time_work:
                            overtime = time_work - hours_average
                            time_work = hours_average
                    if time_work:
                        attendance[dep.id][emp.consecutive_id]['wt'][dat] = str(time_work.seconds // 3600).zfill(2) + ':' + str((time_work.seconds // 60) % 60).zfill(2)
                    if overtime:
                        attendance[dep.id][emp.consecutive_id]['ot'][dat] = str(overtime.seconds // 3600).zfill(2) + ':' + str((overtime.seconds // 60) % 60).zfill(2)

        docargs = {
            'doc_ids': docids,
            'doc_model': self.model,
            'docs': doc,
            'attendance': attendance,
            'departments': departments,
            'dates': dates,
            'att_fields': ['check_in', 'break_out', 'break_in', 'check_out']
        }
        return docargs
