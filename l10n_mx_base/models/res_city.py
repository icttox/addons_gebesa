# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResCountryStateCity(models.Model):
    _inherit = ['res.country.state.city']
    _name = 'res.country.state.city'

    code = fields.Char(
        size=5, help='INEGI code')
