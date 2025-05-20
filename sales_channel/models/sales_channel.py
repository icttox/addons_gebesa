# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class SalesChannel(models.Model):
    _name = 'sales.channel'
    _description = 'Sales channel for invoices'

    name = fields.Char(
        string='Name',
        size=64,
    )

    code = fields.Char(
        string='code',
        size=10,
    )

    description = fields.Text(
        string='Description',
    )

    parent_id = fields.Many2one(
        'sales.channel',
        string='Parent',
    )

    other_income = fields.Boolean(
        string='Other income',
    )
    is_export = fields.Boolean(
        string='It is export',
    )

    active = fields.Boolean(
        string='Active',
        default=True,
    )

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env['res.company']._company_default_get(
            'sales.channel'))
