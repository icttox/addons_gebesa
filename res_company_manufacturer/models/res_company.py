# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    is_manufacturer = fields.Boolean(
        string='Is manufacturer',
        default=False
    )

    sale_project_id = fields.Many2one(
        'account.analytic.account',
        string='Default analytic for sales',
    )

    sale_warehouse_id = fields.Many2one(
        'stock.warehouse',
        string='Default warehouse for sales',
    )
