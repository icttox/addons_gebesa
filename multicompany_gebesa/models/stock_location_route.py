# -*- coding: utf-8 -*-
# Copyright YEAR(S), AUTHOR(S)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class StockLocationRoute(models.Model):
    _inherit = 'stock.location.route'

    company_ids = fields.Many2many(
        'res.company',
        string='Companies',
    )
