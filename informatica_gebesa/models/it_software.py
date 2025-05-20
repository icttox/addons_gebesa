# -*- coding: utf-8 -*-
# © 2021 Leslie Marquez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ItSoftware(models.Model):
    _name = 'it.software'
    _description = 'descripcion pendiente'

    name = fields.Char(
        string='Name',
    )

    merchant = fields.Char(
        string='Merchant',
    )

    function = fields.Text(
        string='Function',
    )
