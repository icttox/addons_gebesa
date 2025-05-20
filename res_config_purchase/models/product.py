# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from ast import literal_eval
from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _default_get_price_account(self):
        res = literal_eval(self.env[
            'ir.config_parameter'].sudo().get_param(
                'purchase_config_settings.purchase_price_account_id'))
        return res

    property_account_creditor_price_difference = fields.Many2one(
        'account.account',
        string='Price Difference Account',
        company_dependent=True,
        default=_default_get_price_account,
        help='This account will be used to value price difference'
               'between purchase price and cost price.'
    )

    @api.model
    def create(self, vals):
        template = super().create(vals)
        generate_account_price = literal_eval(self.env[
            'ir.config_parameter'].sudo().get_param(
                'purchase_config_settings.purchase_price_account_id'))

        template.write({
            'property_account_creditor_price_difference': generate_account_price
        })

        return template
