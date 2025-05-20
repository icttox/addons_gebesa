# -*- coding: utf-8 -*-
# Copyright 2019, Cesar Barron
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class SaleOrder(models.Model):
    _name = 'sale.order'
    _inherit = 'sale.order'

    hubspot_id = fields.Char(
        string='Hubspot ID',
    )

    hubspot_user = fields.Boolean(
        string='Cliente es unidad Hubspot',
        related='partner_id.hubspot_user',
        store=True,
        readonly=True
    )
