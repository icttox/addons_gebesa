# -*- coding: utf-8 -*-
# Copyright 2023, Samuel Barron
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class EmployeeCompanyChangeWizard(models.TransientModel):
    _name = 'employee.company.change.wizard'
    _description = 'Description'

    new_company_id = fields.Many2one(
        'res.company',
        string='New company',
    )

    @api.multi
    def change_company_id(self):
        user_ids = self.env['hr.employee'].browse(self._context.get('active_ids'))
        company_id = self.new_company_id.sudo()
        address = company_id.partner_id.address_get(['default'])
        address_id = address['default'] if address else False
        resource_calendar_id = company_id.resource_calendar_id
        for user in user_ids.sudo():
            for contract in user.contract_ids:
                contract.write({
                    'company_id': company_id.id,
                    'resource_calendar_id': resource_calendar_id.id,
                    'department_id': False,
                    'job_id': False
                })

            user.write({
                'company_id': company_id.id,
                'address_id': address_id,
                'resource_calendar_id': resource_calendar_id.id,
                'department_id': False,
                'job_id': False,
                'parent_id': False,
            })

            user.address_home_id.write({
                'company_id': company_id.id,
            })

            appraisal_ids = self.env['hr.appraisal'].search([
                ('employee_id', '=', user.id)
            ])
            appraisal_ids.write({
                'company_id': company_id.id,
            })

        menu = self.env.ref('hr.menu_open_view_employee_list_my')
        url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        url = url + '/web#action=' + str(menu.action.id) + '&model=hr.employee&view_type=kanban&menu_id=' + str(menu.id)
        return {
            "type": "ir.actions.act_url",
            "url": url,
            "target": "self",
        }
