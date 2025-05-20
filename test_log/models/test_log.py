# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api, fields


class TestLog(models.Model):
    _name = 'test.log'
    _inherit = ['message.post.show.all', 'mail.activity.mixin']

    name = fields.Char(
        string='Name',
    )

    user_id = fields.Many2one(
        'res.users',
        string='Stakeholder',
    )

    priority = fields.Selection([
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('very_high', 'Very High')],
        string='Priority',
    )

    department_id = fields.Many2one(
        'hr.department',
        string='Department',
    )

    description_test = fields.Text(
        string='Test Description'
    )

    expected_results = fields.Text(
        string='Expected results',
    )

    results_obtained = fields.Html(
        string='Results Obtained'
    )

    additional_notes = fields.Text(
        string='Additional Notes'
    )

    status = fields.Selection([
        ('new', 'New'),
        ('process', 'In Process'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')], readonly=True,
        default='new'
    )

    test_execution_date = fields.Datetime(
        string='Test execution date',
    )

    successful_test = fields.Boolean(
        string='Successful test',
    )

    policy_revised = fields.Boolean(
        string='Policy revised by accounting',
    )

    module_id = fields.Many2one(
        'ir.module.module',
        string='Module',
    )

    number_test_request = fields.Integer(
        string='Number of tests requested',
    )

    move_ids = fields.Many2many('account.move', copy=False, string='Moves')

    company_id = fields.Many2one(
        'res.company',
        string='Company',
    )

    @api.multi
    def in_process(self):
        return self.write({'status': 'process'})

    @api.multi
    def prueba_exitosa(self):
        self.successful_test = True
        return self.write({'status': 'done'})

    @api.multi
    def prueba_fallida(self):
        return self.write({'status': 'done'})

    @api.multi
    def policy_revised_accounting(self):
        self.policy_revised = True
