# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from ast import literal_eval
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    perc_revaluation = fields.Float(
        string='Maximum percentage of revaluation'
    )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        get_param = self.env['ir.config_parameter'].sudo().get_param
        perc_revaluation = literal_eval(get_param(
            'mrp_revaluation.perc_revaluation', default='False'))
        res.update(
            perc_revaluation=perc_revaluation,
        )
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        ICPSudo.set_param(
            "mrp_revaluation.perc_revaluation",
            self.perc_revaluation)
