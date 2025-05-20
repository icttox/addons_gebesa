# -*- coding: utf-8 -*-

from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    stc_type_permit = fields.Many2one(
        'l10n.mx.wbl.permit.type',
        string='SCT Type Permit',
    )

    sct_reg = fields.Char(
        string='STC Reg',
    )
