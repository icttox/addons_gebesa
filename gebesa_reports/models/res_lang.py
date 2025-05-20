# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResLang(models.Model):
    _inherit = 'res.lang'

    date_format_pentaho = fields.Char(
        string='Date Format Pentaho',
    )
