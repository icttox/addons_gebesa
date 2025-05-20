# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    ignore_overcredit = fields.Boolean(
        string='Ignore Overcredit',
        help='Ignore Overcredit',
        tracking=True,
    )

    over_credit = fields.Boolean(
        string='Overcredit',
        help='Overcredit',
        compute='_comnpute_overcredit',
    )

    @api.depends('credit', 'credit_limit')
    def _comnpute_overcredit(self):
        for partner in self:
            partner.over_credit = (partner.credit_limit - partner.credit) < 2000
