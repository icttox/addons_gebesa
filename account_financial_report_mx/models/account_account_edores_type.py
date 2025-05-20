# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountAccountEdoresType(models.Model):
    _name = 'account.account.edores.type'
    _inherit = ['message.post.show.all']

    name = fields.Char(
        string='Name',
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )
    cumulative = fields.Boolean(
        string='cumulative',
        default=False,
    )
    sequence = fields.Integer(
        string='Sequence',
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env['res.company']._company_default_get(
            'account.account.edores.type')
    )
    parent_id = fields.Many2one(
        'account.account.edores.type',
        string='Parent',
    )
