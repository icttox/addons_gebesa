# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    numctrl_progress = fields.Integer(
        'Num. Ctrl. Progress',
    )

    folio_progress = fields.Char(
        string='Folio Progress',
    )

    date_progress = fields.Char(
        string='Date Progress',
    )
