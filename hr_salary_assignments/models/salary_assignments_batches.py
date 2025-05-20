from __future__ import division
from odoo import api, fields, models


TYPE_ASSINGS = [
    ('all_employee', 'All employees'),
    ('employee', 'By employee'),
    ('department', 'By department'),
]


class HrSalaryAssingmentsBatches(models.Model):
    _name = 'hr.salary.assingments.batches'

    @api.multi
    def _compute_total(self):
        for record in self:
            record.total_amount = sum(
                [l.assingments_id.total for l in record.line_ids]
            )

    name = fields.Char(required=True)

    company_id = fields.Many2one(
        'res.company', string='Company', readonly=True, copy=False,
        default=lambda self: self.env['res.company']._company_default_get('hr.salary.assingments.batches'),
        states={'draft': [('readonly', False)]})

    struct_id = fields.Many2one(
        'hr.payroll.structure', string='Structure',
        readonly=True, states={'draft': [('readonly', False)]})

    rule_id = fields.Many2one('hr.salary.rule', domain="[('novelty', '=', True)]")

    # rule_ids = fields.One2many('hr.salary.rule', related="struct_id.rule_ids")

    date_assing = fields.Date()

    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In progress'),
        ('validated', 'Validated'),
    ], default="draft")

    filter_assing = fields.Selection(
        TYPE_ASSINGS, default="all_employee")

    department_id = fields.Many2one('hr.department')

    line_ids = fields.One2many(
        'hr.salary.assingments.batches.lines', 'batches_id', copy=False)

    employee_ids = fields.Many2many(
        "hr.employee",
        domain=[
            ('contract_id.state', '=', 'open'),
            ('rfc', '!=', 'XAXX010101000'),
            ('company_id', '!=', False)])

    type_amount = fields.Selection([
        ('manual', 'Manual'),
        ('diario', 'Salario diario según contrato'),
        ('hora', 'Salario por hora segun contrato'),
        ('fijo', 'Importe Fijo')
    ], default="manual")

    fixed_amount = fields.Float('Fixed Amount')

    rate = fields.Float(
        string='Rate (%)',
        # digits='Payroll Rate',
        default=100.0)

    total_amount = fields.Float(
        string='Total',
        compute='_compute_total'
    )

    # type_salary_rule = fields.Selection(related="rule_id.type_salary_rule")

    def domain_type_assing(self):
        domain_model = {
            'employee': ['hr.employee', [('id', 'in', self.employee_ids.ids)], False],

            'all_employee': ['hr.employee', [], False],

            'department': ['hr.employee', [('department_id', '=', self.department_id.id)], False],
        }
        return domain_model

    def _prepare_lines(self, employee_id, rule_id):
        struct_id = (
            self.struct_id or employee_id.contract_id.struct_id)
        contract = employee_id.contract_ids.filtered(
            lambda x: x.state == 'open')
        contract = (
            contract and contract[0] or employee_id.contract_id)

        # dayly_salary = (
        #     (contract.schedule_pay == 'monthly' and
        #         contract.salario_diario) or
        #     (contract.schedule_pay == 'bi-weekly' and
        #         contract.salario_diario) or
        #     (contract.schedule_pay == 'weekly' and
        #         contract.salario_diario))
        # hour_salary = (
        #     (contract.schedule_pay == 'monthly' and
        #         contract.wage_hourly_average) or
        #     (contract.schedule_pay == 'bi-weekly' and
        #         contract.bw_wage_hourly_average) or
        #     (contract.schedule_pay == 'weekly' and
        #         contract.w_wage_hourly_average))
        if self.type_amount == 'manual':
            amount = 0.00
        elif self.type_amount == 'diario':
            amount = 0.00
            # dayly_salary
        elif self.type_amount == 'hora':
            amount = 0.00
            # hour_salary
        elif self.type_amount == 'fijo':
            amount = self.fixed_amount
        date_assing = self.date_assing or fields.date.today()
        vals = {
            'state': 'draft',
            'employee_id': employee_id.id,
            'contract_id': employee_id.contract_id.id,
            'name': ('Salary assings {} {}'.format(
                rule_id.name, employee_id.name)),
            'struct_id': struct_id.id,
            'rate': self.rate,
            'amount': amount,
            'salary_rule_id': rule_id.id,
            'date_assing': date_assing,
            'date_paid': date_assing,
        }
        return vals

    def mandatory_domain(self):
        return [
            ('contract_id.state', '=', 'open'),
            ('rfc', '!=', 'XAXX010101000'),
            ('company_id', '!=', False)
        ]

    def create_lines(self):
        result = []
        for record in self:
            domain = record.domain_type_assing()
            if record.filter_assing not in domain:
                continue
            model, domain, field = domain[record.filter_assing]
            employees = self.env[model].search(
                domain + record.mandatory_domain())
            if field:
                employees = employees.mapped(field)
            for emp in employees:
                vals = record._prepare_lines(emp, record.rule_id)
                result += [(0, 0, vals)]
            record.line_ids = result

    def init_assings(self):
        self.create_lines()
        self.write({'state': 'in_progress'})
        return True

    def validate_assings(self):
        self.write({'state': 'validated'})
        self.line_ids.filtered(lambda x: x.total == 0.00).unlink()
        self.line_ids.filtered(lambda x: x.state != 'validated').write(
            {'state': 'validated'})
        return True


class HrSalaryAssingmentsbatchesLines(models.Model):
    _inherit = 'hr.salary.assingments'
    _name = 'hr.salary.assingments.batches.lines'

    batches_id = fields.Many2one('hr.salary.assingments.batches')

    assingments_id = fields.Many2one('hr.salary.assingments')

    def write(self, vals):
        fields_get = self.env['hr.salary.assingments'].fields_get()
        for record in self:
            new_vals = {}
            if vals.get('state') != 'validated':
                continue
            values = record.read()[0]
            values.pop('id', False)
            for key, val in values.items():
                if key not in fields_get:
                    continue
                ttype = fields_get[key]['type']
                if isinstance(val, (list, tuple)) and ttype in ['many2one']:
                    val = val[0]
                new_vals[key] = val
            res_id = self.env['hr.salary.assingments'].create(
                new_vals)
            res_id.state = 'validated'
            record.assingments_id = res_id.id
        return super().write(vals)
