# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    dev_tipo = fields.Selection(
        [('normal', 'Normal'),
         ('rebilling', 'Rebilling'),
         ('cancellation', 'Cancellation')],
        default='normal',
        string="Type",
        help="defines the type",
    )
