# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class MrpProductColor(models.Model):
    _name = 'mrp.product.color'
    _description = 'Product Color'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    code = fields.Char(
        string='Code',
        track_visibility='onchange',
    )
    name = fields.Char(
        string='Name',
        track_visibility='onchange',
    )

    _sql_constraints = [
        ('code_uniq', 'unique(code)', 'Color code must be unique!'),
    ]
