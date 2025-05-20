# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    am_ids = fields.Many2many('account.move',
                              string='Account Entries',
                              ondelete='restrict',
                              copy=False,
                              index=True)


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    am_ids = fields.Many2many('account.move',
                              string='Account Entries',
                              ondelete='restrict',
                              copy=False,
                              index=True)
