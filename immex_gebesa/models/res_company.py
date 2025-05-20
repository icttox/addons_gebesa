# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    immex_num = fields.Char(
        string='Immex Gebesa',
        copy=False,
    )
    pass_vucem = fields.Text(
        string='Password Vucem',
        copy=False,
    )
    immex_certification_date = fields.Date(
        string='Immex certification date'
    )
