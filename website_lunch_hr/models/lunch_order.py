# Copyright 2022, Cesar Barron
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from datetime import date, timedelta


class LunchOrder(models.Model):
    _inherit = 'lunch.order'

    employee_id = fields.Many2one(
        'hr.employee',
        'Employee',
        states={'new': [('readonly', False)]},
    )

    department_id = fields.Many2one(
        'hr.department',
        string='Department',
        related='employee_id.department_id',
        readonly=True,
        store=True,
    )

    employee_comp_id = fields.Many2one(
        'res.company',
        string='Company employee',
        related='employee_id.company_id',
        readonly=True,
        store=True,
    )

    @api.constrains('employee_id', 'date')
    def _check_unique_employee_for_day(self):
        for lunch in self:
            lunch_ids = self.search([
                ('employee_id', '=', lunch.employee_id.id),
                ('date', '=', lunch.date),
                ('id', '!=', lunch.id)])
            if lunch_ids:
                raise ValidationError(
                    "Ya se registro una comida el dia de hoy para el empleado %s, por favor de comunicarse son Recursos Humanos" % lunch.employee_id.name)


class LunchOrderLine(models.Model):
    _inherit = 'lunch.order.line'

    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        related='order_id.employee_id',
        readonly=True,
        store=True
    )

    salary_assign_ids = fields.Many2many(
        'hr.salary.assingments',
        string='Created salary assingments',
    )

    was_printed = fields.Boolean(
        string='Was printed',
        default=False
    )

    def create_salary_assignment(self):
        data = self._get_total_meals_last_week()

        for key, val in data.items():
            assings = []
            employee = self.env['hr.employee'].browse([key])
            datsr = ', '.join(str(strdata) for strdata in val[1])
            orders = ', '.join(x.display_name for x in map(
                lambda order: self.env['lunch.order'].browse([order]), val[2]))
            lines = [x for x in map(
                lambda linea: self.env['lunch.order.line'].browse([linea]), val[3])]
            rule_comedor = self.env.ref('website_lunch_hr.prevision_social_comedor')
            rule_otras_ret = self.env.ref('website_lunch_hr.otras_retenciones')
            meal_data = {
                'employee_id': employee.id,
                'contract_id': employee.contract_id.id,
                'name': 'Consumo comedor: ' + datsr,
                'amount': len(val[1]) * 19.50,
                'note': 'Consumo comedor dias: ' + datsr + '. Ordenes: ' + orders,
                'salary_rule_id': rule_comedor.id,
                'date_assing': val[4],
                'date_paid': val[4],
                'state': 'validated',
            }

            assign_meal = self.env['hr.salary.assingments'].create(meal_data)
            assings.append(assign_meal.id)

            other_ret_meal = {
                'employee_id': employee.id,
                'contract_id': employee.contract_id.id,
                'name': 'Otras retenciones: ' + datsr,
                'amount': len(val[1]) * 14.50,
                'note': 'Otras retenciones dias: ' + datsr + '. Ordenes: ' + orders,
                'salary_rule_id': rule_otras_ret.id,
                'date_assing': val[4],
                'date_paid': val[4],
                'state': 'validated',
            }

            assign_other_ret = self.env['hr.salary.assingments'].create(other_ret_meal)
            assings.append(assign_other_ret.id)
            for linea in lines:
                linea.write({'salary_assign_ids': [(4, x) for x in assings]})

    def _get_total_meals_last_week(self):
        today = date.today()
        end = today - timedelta(days=today.weekday() + 1)
        start = end - timedelta(days=6)
        date_assing = end - timedelta(days=2)

        grouped_meals = self.env['lunch.order.line'].sudo().read_group([
            ('date', '>=', start),
            ('date', '<=', end),
            ('state', '=', 'confirmed'),
            ('salary_assign_ids', '=', False)
        ],
            [
            'employee_id',
            'price',
            'dates:array_agg(date)',
            'orders:array_agg(order_id)',
            'lines:array_agg(id)',
        ], ['employee_id'], orderby='id')

        result = dict((data['employee_id'][0], (
            data['price'],
            data['dates'],
            data['orders'],
            data['lines'],
            date_assing)) for data in grouped_meals)
        return result
