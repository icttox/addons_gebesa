# Copyright 2021, Leslie Lillian
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class ResPartnerDealer(models.Model):
    _name = 'res.partner.dealer'
    _description = 'Partner dealer'

    name = fields.Char(
        string='Name',
        required=True,
    )

    active = fields.Boolean(
        string='Active',
        default=True,
        required=True,
    )

    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        required=True,
    )

    dealer_type = fields.Selection(
        [('normal', 'Normal'),
         ('strategic', 'Strategic')],
        string="Dealer type",
        default='normal',
    )
