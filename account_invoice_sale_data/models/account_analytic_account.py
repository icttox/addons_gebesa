# -*- coding: utf-8 -*-
# © 2016 Cesar Barron
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    journal_sale_id = fields.Many2one(
        'account.journal',
        string='Default sale journal',
        help='Default sale journal for this analytic',
    )
