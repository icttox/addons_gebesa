from __future__ import division
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

PRELOAD_FIELD = ['contract_id', 'struct_id', 'name']


class HrSalaryAssingments(models.Model):
    _name = 'hr.salary.assingments'

    name = fields.Char(required=True)

    salary_rule_id = fields.Many2one(
        'hr.salary.rule', string='Rule', domain="[('novelty', '=', True)]", required=True)

    code = fields.Char(related="salary_rule_id.code")

    category_id = fields.Many2one(related="salary_rule_id.category_id")

    date_assing = fields.Date(default=fields.Date.today())

    date_paid = fields.Date(
        default=fields.Date.today(), string="Payment date")

    slip_id = fields.Many2one(
        'hr.payslip', string='Pay Slip', required=False, ondelete=False)

    struct_id = fields.Many2one(
        'hr.payroll.structure', string='Structure',
        readonly=True, states={'draft': [('readonly', False)]})

    state = fields.Selection([
        ('draft', 'Draft'),
        ('validated', 'Validated'),
        ('reserved', 'Reserved'),
        ('paid', 'Paid'),
        ('cancel', 'Cancel'),
    ], default="draft")

    # rule_ids = fields.One2many('hr.salary.rule', related="struct_id.rule_ids")

    employee_id = fields.Many2one(
        'hr.employee', string='Employee', required=True)

    contract_id = fields.Many2one(
        'hr.contract', string='Contract', required=True, index=True)

    rate = fields.Float(
        string='Rate (%)',
        # digits='Payroll Rate',
        default=100.0)

    # type_salary_rule = fields.Selection(related="salary_rule_id.type_salary_rule")
    amount = fields.Float()
    quantity = fields.Float(
        # digits='Payroll',
        default=1.0)

    total = fields.Float(
        compute='_compute_total',
        string='Total',
        # digits='Payroll',
        store=True)

    note = fields.Text(string='Description')

    sequence = fields.Integer(required=True, index=True, default=5,
                              help='Use to arrange calculation sequence')

    type_amount = fields.Selection([
        ('manual', 'Manual'),
        ('diario', 'Salario diario según contrato'),
        ('hora', 'Salario por hora segun contrato'),
    ], default="manual")

    credit_note = fields.Boolean(
        readonly=True,
        help="Indicates this salary assingments has a refund of another")

    department_id = fields.Many2one(
        related="employee_id.department_id",
        string='Department',
        store=True
    )

    employee_comp_id = fields.Many2one(
        'res.company',
        string='Company employee',
        related='employee_id.company_id',
        readonly=True,
        store=True,
    )

    employee_identification_id = fields.Char(
        string='Identification employee',
        related='employee_id.identification_id',
        readonly=True,
        store=True,
    )

    days = fields.Integer(
        string='Days',
    )

    # @api.onchange('type_amount')
    # def onchange_type_amount(self):
    #     for record in self:
    #         if not record.employee_id:
    #             continue
    #         contract = record.employee_id.contract_ids.filtered(
    #             lambda x: x.state == 'open')
    #         contract = (
    #             contract and contract[0] or
    #             record.employee_id.contract_id)
    #         dayly_salary = self._calculate_dayly_salary(contract)
    #         hour_salary = self._calculate_hour_salary(contract)
    #         if self.type_amount == 'diario':
    #             self.amount = dayly_salary
    #         elif self.type_amount == 'hora':
    #             self.amount = hour_salary

    @api.depends('quantity', 'amount', 'rate')
    def _compute_total(self):
        for line in self:
            line.total = float(line.quantity) * line.amount * line.rate / 100

    @api.model
    def create(self, vals):
        for key in PRELOAD_FIELD:
            if key not in vals:
                vals[key] = getattr(self, 'default_' + key)(
                    vals['employee_id'])
        contract = vals.get('contract_id', False)
        new_contract = False
        employee_id = self.env['hr.employee'].browse(vals.get(
            'employee_id'))
        if not contract:
            contract = employee_id.contract_id if employee_id else False
        else:
            contract = self.env['hr.contract'].browse(contract)
            new_contract = employee_id.contract_ids.filtered(
                lambda c: c.name == contract.name)
        if not contract and not new_contract:
            raise ValidationError(
                _("Employee %s has no contract." % (employee_id.name)))
        vals['contract_id'] = contract.id or new_contract[0].id
        # if vals.get('type_amount') in ('diario', 'hora'):
        #     contract = employee_id.contract_ids.filtered(
        #         lambda x: x.state == 'open')
        #     contract = (contract and contract[0] or employee_id.contract_id)
        #     dayly_salary = self._calculate_dayly_salary(contract)
        #     hour_salary = self._calculate_hour_salary(contract)
        #     vals['amount'] = dayly_salary if vals.get('type_amount') == \
        #         'diario' else hour_salary
        return super().create(vals)

    def get_employee(self, employee_id, field):
        employee_obj = self.env['hr.employee']
        fields_get = employee_obj.fields_get()
        if not employee_id or field not in fields_get:
            return False
        employee = employee_obj.browse(employee_id)
        field_value = getattr(employee, field)
        return field_value

    def default_contract_id(self, employee_id):
        contract_id = self.get_employee(employee_id, 'contract_id')
        return contract_id and contract_id.id

    def default_struct_id(self, employee_id):
        contract_id = self.get_employee(employee_id, 'contract_id')
        struct_id = contract_id and contract_id.struct_id.id or False
        return struct_id

    def default_name(self, employee_id):
        name = self.get_employee(employee_id, 'name')
        name = "Salary assignment to {}".format(name)
        return name

    @api.onchange('employee_id')
    def onchange_contract_id(self):
        for record in self:
            if not record.employee_id:
                continue
            contract_id = record.employee_id.contract_ids.filtered(
                lambda x: x.state == 'open')
            contract_id = (
                contract_id and contract_id[0] or
                record.employee_id.contract_id)
            record.contract_id = contract_id.id
            record.struct_id = contract_id.struct_id.id

    def validate(self):
        records = self.filtered(lambda x: x.state == 'draft')
        return records.write({'state': 'validated'})

    def cancel(self):
        records = self.filtered(lambda x: x.state == 'validated')
        return records.write({'state': 'cancel'})

    def reset_draft(self):
        records = self.filtered(lambda x: x.state == 'cancel')
        return records.write({'state': 'draft'})

    # def _calculate_dayly_salary(self, contract):
    #     schedule_pay = contract.structure_type_id.default_schedule_pay
    #     dayly_salary = (
    #         (schedule_pay == 'monthly' and
    #             contract.wage_daily_average) or
    #         (schedule_pay == 'bi-weekly' and
    #             contract.bw_wage_daily_average) or
    #         (schedule_pay == 'weekly' and
    #             contract.w_wage_daily_average))
    #     return dayly_salary

    # def _calculate_hour_salary(self, contract):
    #     schedule_pay = contract.structure_type_id.default_schedule_pay
    #     hour_salary = (
    #         (schedule_pay == 'monthly' and contract.wage_hourly_average) or
    #         (schedule_pay == 'bi-weekly' and contract.bw_wage_hourly_average) or
    #         (schedule_pay == 'weekly' and contract.w_wage_hourly_average))
    #     return hour_salary
