# -*- coding: utf-8 -*-
# © <2018> <Aldo Nerio>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import re
from odoo import _, fields, models, api
from odoo.exceptions import ValidationError, UserError


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    consecutive_id = fields.Char(
        string='No. Employee'
    )

    rfc = fields.Char(
        string='RFC',
    )

    curp = fields.Char(
        string='CURP',
    )

    escolaridad = fields.Selection(
        [('primaria', 'Primary School'),
         ('secundaria', 'Medium School'),
         ('preparatoria', 'Hight School'),
         ('licenciatura', 'Bachelors Degree'),
         ('postgrado', 'Postgraduate')],
        string='Scholarship',
    )

    spouse = fields.Char(
        string='Spouse',
    )

    father = fields.Char(
        string='Father',
    )

    mother = fields.Char(
        string='Mother',
    )

    imss = fields.Char(
        string='No. IMSS',
    )

    reingreso = fields.Boolean(
        string='Re-Entry',
        default=False
    )

    sindicalizado = fields.Boolean(
        string='Sindicalizado',
        default=False
    )

    antiguedad_vivienda = fields.Char(
        string='Antique Housing',
    )

    umf = fields.Integer(
        string='UMF',
    )

    beneficio_1 = fields.Char(
        string='Beneficiary First',
    )

    beneficio_2 = fields.Char(
        string='Beneficiary Second',
    )

    porcentaje_1 = fields.Float(
        string='First Percentage',
    )

    porcentaje_2 = fields.Float(
        string='Second Percentage',
    )

    entry_date_vacation = fields.Date(
        string='Entry date for vacation'
    )

    days_available_holidays = fields.Float(
        string='Days available for holidays',
        compute='_compute_days_available_holidays'
    )

    resource_calendar_ids = fields.Many2many(
        'resource.calendar',
        string='Switch working hours',
    )

    age = fields.Integer(
        string='Edad',
        compute='_compute_age',
        store=True,
    )

    @api.depends('birthday')
    def _compute_age(self):
        for record in self:
            if record.birthday:
                date_today = fields.Date.today()
                date_age = date_today - record.birthday
                date_in_years = date_age.days / 365
                record.age = int(date_in_years)
            else:
                record.age = 0

    _sql_constraints = [
        ('consecutive_id_uniq', 'unique (consecutive_id)',
         'This field must be unique!')
    ]

    @api.model
    def schedule_rotation(self):
        employees = self.search([
            ('resource_calendar_ids', '!=', False)])
        for emp in employees:
            for resource in emp.resource_calendar_ids:
                if resource.id == emp.resource_calendar_id.id:
                    continue
                emp.resource_calendar_id = resource.id
                break

    @api.multi
    def _compute_days_available_holidays(self):
        for employee in self:
            leave_type = self.env['hr.leave.type'].with_context(
                employee_id=employee.id).sudo().search([
                    ('allocation_type', '!=', 'no')])
            days = 0
            for lea_type in leave_type:
                days += lea_type.virtual_remaining_leaves
            employee.days_available_holidays = days

    @api.constrains('porcentaje_1', 'porcentaje_2')
    def _check_total_percentage(self):
        for empleado in self:
            if not (empleado.porcentaje_2 + empleado.porcentaje_1) == 100:
                raise ValidationError(_('The sum o the percentage'
                                        '\n Must be 100 '))

    @api.model
    def create_leave_allocation(self):
        current_year = fields.Date.from_string(fields.Date.today()).year
        type_allocation = self.env.ref('rh_gebesa.holiday_by_law')
        for employee in self.search([('entry_date_vacation', '!=', False)]):
            year_entry = fields.Date.from_string(
                employee.entry_date_vacation).year
            year = current_year - year_entry
            holidays = 0
            if year == 1:
                holidays = 12
            elif year == 2:
                holidays = 14
            elif year == 3:
                holidays = 16
            elif year == 4:
                holidays = 18
            elif year == 5:
                holidays = 20
            elif 6 <= year <= 10:
                holidays = 22
            elif 11 <= year <= 15:
                holidays = 24
            elif 16 <= year <= 20:
                holidays = 26
            elif 21 <= year <= 25:
                holidays = 28
            elif 26 <= year <= 30:
                holidays = 30
            elif 31 <= year <= 36:
                holidays = 32

            if holidays > 0:
                allocation = self.env['hr.leave.allocation'].with_context(
                    import_file=True).create({
                        'name': employee.name + _(' vacation for ') + str(
                            year) + _(' year of work'),
                        'number_of_days': holidays,
                        'holiday_type': 'employee',
                        'employee_id': employee.id,
                        'holiday_status_id': type_allocation.id,
                    })
                if allocation.message_follower_ids:
                    allocation.message_follower_ids.unlink()
                allocation.action_validate()

    @api.model
    def create(self, vals):
        if 'consecutive_id' not in vals.keys():
            vals['consecutive_id'] = self.env['ir.sequence'].next_by_code(
                'empleado') or '/'
            if not 'identification_id' not in vals.keys() and vals['consecutive_id'] != '/':
                vals['identification_id'] = vals['consecutive_id'].split('-')[1]
        # res = {'value': {'consecutive_id': codigo}}
        return super().create(vals)

    @api.multi
    def send_id(self):
        return {
            'name': _('Employee Consecutive Forchange'),
            'type': 'ir.actions.act_window',
            'res_model': 'employee.consecutive.forchange.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': self._context,
        }

    @api.multi
    def company_change_geb(self):
        return {
            'name': _('Employee Change Of Company'),
            'type': 'ir.actions.act_window',
            'res_model': 'employee.company.change.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': self._context,
        }

    @api.constrains('curp', 'rfc', 'imss')
    def _check_validate_fields(self):
        # pattern_curp = re.compile("([A-Z]{4}[0-9]{6}[H,M][A-Z]{5}[0-9]{2}$)")

        path_curp = "([A-Z]{1}[AEIOU]{1}[A-Z]{2}[0-9]{2}(0[1-9]|1[0-2])"
        path_curp += "(0[1-9]|1[0-9]|2[0-9]|3[0-1])[HM]{1})"
        path_curp += "(AS|BC|BS|CC|CS|CH|CL|CM|DF|DG|GT|GR|HG|JC|MC|MN|MS|NT|"
        path_curp += "NL|OC|PL|QT|QR|SP|SL|SR|TC|TS|TL|VZ|YN|ZS|NE)"
        path_curp += "[B-DF-HJ-NP-TV-Z]{3}[0-9A-Z]{1}[0-9]{1}"
        pattern_curp = re.compile(path_curp)

        pattern_rfc = re.compile("([A-Z]{4}[0-9]{6}[A-Z0-9]{3}$)")
        pattern_imss = re.compile("([0-9]{11}$)")

        if self.curp:
            if not pattern_curp.match(self.curp):
                raise UserError(_("Please enter valid CURP"))

        if self.rfc:
            if not pattern_rfc.match(self.rfc):
                raise UserError(_("Please enter valid RFC"))

        if self.imss:
            if not pattern_imss.match(self.imss):
                raise UserError(_("Please enter valid IMSS"))

    @api.multi
    def toggle_active(self):
        res = super().toggle_active()

        mail_obj = self.env['mail.mail']

        for empleado in self:
            if not empleado.active:
                for contract in empleado.contract_ids:
                    contract.state = 'cancel'
                    contract.date_end = fields.Date.today()

                body_mail = u"""
                    Favor de recolectar la responsiva del empleado: %s
                    <br/>
                    Usuario de erp: %s
                  """ % (empleado.name, empleado.user_id.name)

                mail = mail_obj.create({
                    'subject': 'Responsiva ' + empleado.name,
                    'email_to': 'soportec@gebesa.com',
                    'headers': "{'Return-Path': u'odoo@gebesa.com'}",
                    'body_html': body_mail,
                    'auto_delete': True,
                    'message_type': 'comment',
                })
                mail.send()

        return res
