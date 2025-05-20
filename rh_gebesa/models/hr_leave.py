# -*- coding: utf-8 -*-
# © <2021> <Samuel Barron>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class HrLeave(models.Model):
    _inherit = 'hr.leave'

    for_payroll = fields.Boolean(
        string='For payment by payroll',
    )
