# -*- coding: utf-8 -*-
# Copyright 2022, Marco Esquivel
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    sellers_ids = fields.Many2many(
        'res.users',
        string='Vendedores',
    )
