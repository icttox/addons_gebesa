# -*- coding: utf-8 -*-
# © <2018> <Aldo Nerio>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models
# from odoo.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    dealer_id = fields.Many2one(
        'res.partner',
        string='Dealer',
        # track_visibility=True,
    )

    partner_dealer_id = fields.Many2one(
        'res.partner.dealer',
        string='Partner Dealer',
        required=False,
    )
    requires_dealer = fields.Boolean(
        string='Requires dealer',
        related="partner_id.requires_dealer"
    )
