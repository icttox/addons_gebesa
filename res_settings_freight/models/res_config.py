# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    freight_account_id = fields.Many2one(
        'account.account',
        string='Default account freight',
        related='company_id.freight_account_id',
        readonly=False,
    )

    installation_account_id = fields.Many2one(
        'account.account',
        string='Default account installation',
        related='company_id.installation_account_id',
        readonly=False,
    )

    return_account_id = fields.Many2one(
        'account.account',
        string='Default account sales return',
        related='company_id.return_account_id',
        readonly=False,
    )

    # @api.model
    # def get_values(self):
    #     res = super(ResConfigSettings, self).get_values()
    #     get_param = self.env['ir.config_parameter'].sudo().get_param
    #     freight_account_id = literal_eval(get_param(
    #         'res_settings_freight.freight_account_id', default='False'))
    #     installation_account_id = literal_eval(get_param(
    #         'res_settings_freight.installation_account_id', default='False'))
    #     return_account_id = literal_eval(get_param(
    #         'res_settings_freight.return_account_id', default='False'))
    #     res.update(
    #         freight_account_id=freight_account_id,
    #         installation_account_id=installation_account_id,
    #         return_account_id=return_account_id,
    #     )
    #     return res

    # @api.multi
    # def set_values(self):
    #     super(ResConfigSettings, self).set_values()
    #     ICPSudo = self.env['ir.config_parameter'].sudo()
    #     ICPSudo.set_param(
    #         "res_settings_freight.freight_account_id",
    #         self.freight_account_id.id)
    #     ICPSudo.set_param(
    #         "res_settings_freight.installation_account_id",
    #         self.installation_account_id.id)
    #     ICPSudo.set_param(
    #         "res_settings_freight.return_account_id",
    #         self.return_account_id.id)
