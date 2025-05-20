# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    deprecated_city_id = fields.Many2one(
        'res.country.state.city',
        string='City',
        readonly=True,
        related='partner_shipping_id.city_deprecated_id'
    )

    city_id = fields.Many2one(
        'res.city',
        string='City',
        readonly=True,
        related='partner_shipping_id.city_id'
    )

    state_id = fields.Many2one(
        'res.country.state',
        string='State',
        readonly=True,
        related='partner_shipping_id.state_id'
    )

    country_id = fields.Many2one(
        'res.country',
        string='Country',
        readonly=True,
        related='partner_shipping_id.country_id'
    )
