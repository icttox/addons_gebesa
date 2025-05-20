# -*- coding: utf-8 -*-
# © <2018> <Aldo Nerio>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class HrDepartment(models.Model):
    _inherit = 'hr.department'

    analytic_id = fields.Many2one(
        'account.analytic.account',
        string='Cost Center'
    )
