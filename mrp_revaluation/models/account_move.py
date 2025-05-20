# -*- coding: utf-8 -*-
# © <2022> <Samuel Barron>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountMoveLine(models.Model):
    _name = "account.move"
    _inherit = "account.move"

    location_id = fields.Many2one(
        'stock.location',
        string='Location',
    )
