# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    covid_vacination = fields.Selection(
        [
            ('none', 'Ninguna'),
            ('first', 'Primera Dosis'),
            ('second', 'Segunda Dosis'),
            ('unique', 'Unica Dosis')],
        string='Covid Vacination'
    )
