# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    advance_tax_id = fields.Many2one(
        'account.tax',
        string='Default Advance Tax',
    )

    advance_tax_cust_id = fields.Many2one(
        'account.tax',
        string='Default Advance Tax Customer',
    )
