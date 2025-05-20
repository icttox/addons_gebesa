# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class MrpOperation(models.Model):
    _inherit = 'mrp.operation'

    daily_load_available_op = fields.Boolean(
        string="Daily Load Available"
    )
