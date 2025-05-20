# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from ast import literal_eval
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    purchase_price_account_id = fields.Many2one(
        'account.account',
        string='Default Account Purchase Price Difference',
    )

    @api.model
    def get_values(self):
        res = super().get_values()
        get_param = self.env['ir.config_parameter'].sudo().get_param
        purchase_price_account_id = literal_eval(get_param(
            'purchase_config_settings.purchase_price_account_id',
            default='False'))
        res.update(
            purchase_price_account_id=purchase_price_account_id,
        )
        return res

    @api.multi
    def set_values(self):
        super().set_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        ICPSudo.set_param(
            "purchase_config_settings.purchase_price_account_id",
            self.purchase_price_account_id.id)
