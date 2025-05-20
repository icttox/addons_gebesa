# -*- coding: utf-8 -*-

from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    apikey = fields.Char(
        related='company_id.apikey',
        readonly=False)


class ResCompany(models.Model):
    _inherit = 'res.company'

    apikey = fields.Char(
        string='API KEY')
