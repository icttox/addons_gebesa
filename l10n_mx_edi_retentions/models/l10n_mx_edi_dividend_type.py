# -*- coding: utf-8 -*-

from odoo import models, fields


class L10nMxEdiDividendOrProfitablenessType(models.Model):
    _name = 'l10n_mx_edi.dividend.or.profitableness.type'

    code = fields.Char(
        string='Code',
    )
    name = fields.Char(
        string='Name',
    )
