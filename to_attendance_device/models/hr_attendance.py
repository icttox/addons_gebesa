from datetime import date, timedelta, datetime
from odoo import models, fields, api
import pytz


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    break_out = fields.Datetime(
        string='Break-out',
    )
    break_in = fields.Datetime(
        string='Break-in',
    )
    date = fields.Date(
        string='Date',
        compute='_compute_date',
        store=True
    )
    user_attendance_ids = fields.One2many(
        'user.attendance',
        'hr_attendance_id',
        string='User attendance',
    )
    checkin_device_id = fields.Many2one('attendance.device', string='Checkin Device', readonly=True, index=True,
                                        help='The device with which user took check in action')
    checkout_device_id = fields.Many2one('attendance.device', string='Checkout Device', readonly=True, index=True,
                                         help='The device with which user took check out action')
    activity_id = fields.Many2one('attendance.activity', string='Attendance Activity',
                                  help='This field is to group attendance into multiple Activity (e.g. Overtime, Normal Working, etc)')

    @api.constrains('check_in', 'check_out', 'employee_id')
    def _check_validity(self):
        if not self.env.context.get('synch_ignore_constraints', False):
            super(HrAttendance, self)._check_validity()

    @api.depends('check_in', 'break_out', 'break_in', 'check_out')
    def _compute_date(self):
        for att in self:
            date = att.check_in or att.break_out or att.break_in or att.check_out

            date = fields.Datetime.context_timestamp(
                att, date)

            att.date = date.strftime('%Y-%m-%d')

    @api.depends('check_in', 'break_out', 'break_in', 'check_out')
    def _compute_worked_hours(self):
        for attendance in self:
            if attendance.check_out:
                time = timedelta(hours=attendance.employee_id.resource_calendar_id.start_hour)
                timezone = pytz.timezone(self.env.user.tz)
                check_in = datetime(
                    year=attendance.date.year,
                    month=attendance.date.month,
                    day=attendance.date.day,
                    hour=int(time.total_seconds() // 3600.0),
                    minute=int((time.total_seconds() % 3600) / 60),
                    second=0,
                )
                check_in = timezone.localize(check_in).astimezone(pytz.UTC).replace(tzinfo=None)

                if check_in < attendance.check_in:
                    check_in = attendance.check_in

                delta = attendance.check_out - check_in
                delta_break = timedelta(minutes=attendance.employee_id.resource_calendar_id.break_time * 60)
                if attendance.break_out and attendance.break_in:
                    delta_break_real = attendance.break_in - attendance.break_out
                    if delta_break_real > delta_break:
                        delta_break = delta_break_real

                # import ipdb; ipdb.set_trace()
                delta = delta - delta_break
                attendance.worked_hours = delta.total_seconds() / 3600.0

    def create_salary_assignment(self):
        rule_overtime = self.env.ref('to_attendance_device.horas_extras')
        rule_basic = self.env.ref('hr_payroll.hr_rule_basic')

        dic_max_ov = {
            1: 5,
            2: 4,
            3: 2,
            4: 1,
            5: 0
        }

        today = date.today()
        end = today - timedelta(days=today.weekday() + 1)
        start = end - timedelta(days=6)
        date_assing = end - timedelta(days=2)

        attendances = self.search([
            ('date', '>=', start),
            ('date', '<=', end)])

        for employee in attendances.mapped('employee_id'):
            if not employee.active:
                continue

            atte_emp = attendances.filtered(
                lambda att: att.employee_id.id == employee.id)
            overtime = 0
            days = 0
            leave = 5
            calendar_hours_per_day = timedelta(
                hours=employee.resource_calendar_id.hours_per_day)
            days_work = employee.resource_calendar_id.attendance_ids.mapped('dayofweek')
            delta_break = timedelta(minutes=employee.resource_calendar_id.break_time * 60)
            limit_overtime = employee.contract_id.max_overtime

            if limit_overtime <= 0:
                continue

            for atte in atte_emp:
                day_week = str(atte.date.weekday())
                check_in_status = atte.user_attendance_ids.filtered(lambda r: r.timestamp == atte.check_in).status
                is_all_overtime = False
                if day_week not in days_work:
                    if check_in_status != 7:
                        is_all_overtime = True

                new_overtime = 0

                if not is_all_overtime:
                    leave -= 1
                    if atte.worked_hours > 0.00:
                        hours_average = timedelta(minutes=(atte.worked_hours * 60))
                        hours_per_day = calendar_hours_per_day
                        if check_in_status == 7:
                            hours_per_day = timedelta(hours=7)
                            hours_average += delta_break
                        if hours_per_day < hours_average:
                            days = days + 1
                            delta = (hours_average - hours_per_day).seconds
                            new_overtime = delta // 3600
                            overtime_res = delta % 3600
                            if overtime_res >= 2700:
                                new_overtime += 1

                else:
                    check_in = atte.check_in
                    check_out = atte.check_out
                    if not check_out:
                        if atte.break_in:
                            check_out = atte.break_in
                        else:
                            check_out = atte.break_out
                    if check_in and check_out:
                        delta = check_out - check_in
                        if delta.total_seconds() > 0:
                            new_overtime = delta.total_seconds() // 3600.0
                            overtime_res = delta.total_seconds() % 3600
                            if overtime_res >= 2700:
                                new_overtime += 1

                overtime += new_overtime

            if overtime > limit_overtime:
                overtime = limit_overtime

            max_overtime = 9
            if leave in dic_max_ov:
                max_overtime = dic_max_ov[leave]

            assign_qty = overtime
            if assign_qty > max_overtime:
                assign_qty = max_overtime
            overtime = overtime - assign_qty

            if days > 5:
                days = 5

            if assign_qty > 0:
                assign_data = {
                    'employee_id': employee.id,
                    'contract_id': employee.contract_id.id,
                    'name': 'Tiempo Extra',
                    'quantity': assign_qty,
                    'amount': employee.contract_id.salario_hora * 2,
                    'note': 'Tiempo Extra: ' + str(assign_qty) + ' hora(s)',
                    'salary_rule_id': rule_overtime.id,
                    'days': days,
                    'date_assing': date_assing,
                    'date_paid': date_assing,
                    'state': 'validated',
                }
                self.env['hr.salary.assingments'].create(assign_data)

            if overtime > 0:
                assign_data = {
                    'employee_id': employee.id,
                    'contract_id': employee.contract_id.id,
                    'name': 'Tiempo Extra 2',
                    'quantity': overtime,
                    'amount': employee.contract_id.salario_hora * 2,
                    'note': 'Tiempo Extra 2: ' + str(overtime) + ' hora(s)',
                    'salary_rule_id': rule_basic.id,
                    'days': days,
                    'date_assing': date_assing,
                    'date_paid': date_assing,
                    'state': 'validated',
                }
                self.env['hr.salary.assingments'].create(assign_data)
