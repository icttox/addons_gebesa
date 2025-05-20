# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    move_untaxed_id = fields.Many2one(
        'account.move',
        string='Account entry untaxed',
    )

    move_tax_ids = fields.One2many(
        'account.move',
        'move_untaxed_id',
        string='Taxes',
    )


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    diot = fields.Boolean(
        string='Diot',
    )
