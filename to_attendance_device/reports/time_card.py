# Copyright 2022, Samuel Barron
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, models
from datetime import timedelta


class ReportTimeCard(models.AbstractModel):
    _name = 'report.to_attendance_device.report_time_card'
    _description = 'Report Time Card'

    @api.multi
    def _get_report_values(self, docids, data=None):
        self.model = 'attendance.reports.wizard'
        doc = self.env[self.model].browse(docids)
        attendances = {}
        # dic_employees = {}
        dates = []

        delta = doc.end_date - doc.start_date
        for dat in range(delta.days + 1):
            dates += [doc.start_date + timedelta(days=dat)]

        domain_department = doc.get_domain_department()
        domain_employee = doc.get_domain_employee()
        departments = self.env['hr.department'].search(domain_department)

        domain = [('date', '>=', doc.start_date), ('date', '<=', doc.end_date)]
        # atte = self.env['hr.attendance'].search(
        #     domain, order="check_in asc")

        for dep in departments:
            # employees = atte.mapped('employee_id').filtered(
            #     lambda emp: emp.department_id.id == dep.id)
            employees = self.env['hr.employee'].search(
                domain_employee + [('department_id', '=', dep.id)],
                order="consecutive_id asc")
            if employees:
                attendances[dep.id] = {}

                for emp in employees:
                    # dic_employees[emp.id] = emp
                    # att_employee = atte.filtered(
                    #     lambda attendance: attendance.employee_id.id == emp.id)
                    att_employee = self.env['hr.attendance'].search(
                        domain + [('employee_id', '=', emp.id)], order="check_in asc")

                    attendances[dep.id][emp.consecutive_id] = {
                        'att': {},
                        'emp': emp,
                        'lea': {},
                    }
                    for dat in dates:
                        attendances[dep.id][emp.consecutive_id]['att'][dat] = att_employee.filtered(
                            lambda attendance: attendance.date == dat)

                        leave = self.env['hr.leave'].search([
                            ('employee_id', '=', emp.id),
                            ('request_date_from', '<=', dat),
                            ('request_date_to', '>=', dat)])
                        attendances[dep.id][emp.consecutive_id]['lea'][dat] = leave

        # employees = atte.mapped('employee_id').filtered(
        #     lambda emp: not emp.department_id)
        employees = self.env['hr.employee'].search(
            [('department_id', '=', False),
             ('company_id', '=', self.env.user.id),
             ('rfc', '!=', 'XAXX010101000')])
        if employees:
            attendances[0] = {}
            for emp in employees:
                # dic_employees[emp.id] = emp
                # att_employee = atte.filtered(
                #     lambda attendance: attendance.employee_id.id == emp.id)
                att_employee = self.env['hr.attendance'].search(
                    domain + [('employee_id', '=', emp.id)], order="check_in asc")

                attendances[0][emp.consecutive_id] = {
                    'att': {},
                    'emp': emp,
                    'lea': {},
                }
                for dat in dates:
                    attendances[0][emp.consecutive_id]['att'][dat] = att_employee.filtered(
                        lambda attendance: attendance.date == dat)

                    leave = self.env['hr.leave'].search([
                        ('employee_id', '=', emp.id),
                        ('request_date_from', '<=', dat),
                        ('request_date_to', '>=', dat)])
                    attendances[0][emp.consecutive_id]['lea'][dat] = leave

        docargs = {
            'doc_ids': docids,
            'doc_model': self.model,
            'docs': doc,
            'dates': dates,
            'attendances': attendances,
            'departments': departments,
            # 'employees': dic_employees,
        }
        return docargs
