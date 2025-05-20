# -*- coding: utf-8 -*-

from odoo import models, fields


class L10nMxEdiRetentionsType(models.Model):
    _name = 'l10n_mx_edi.retentions.type'

    code = fields.Char(
        string='Code',
    )
    name = fields.Char(
        string='Name',
    )
