# -*- coding: utf-8 -*-

from odoo import models, fields


class L10nMxEdiTaxpayerType(models.Model):
    _name = 'l10n_mx_edi.taxpayer.type'

    code = fields.Char(
        string='Code',
    )
    name = fields.Char(
        string='Name',
    )
