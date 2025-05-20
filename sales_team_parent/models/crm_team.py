# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class CrmTeam(models.Model):
    _inherit = 'crm.team'

    parent_id = fields.Many2one(
        'crm.team',
        string='Parent Team',
        help='Sales Team Parent',
    )
