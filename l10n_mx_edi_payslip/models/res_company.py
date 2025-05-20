# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    l10n_mx_edi_curp = fields.Char(
        'CURP', size=18, help='Attribute to set in XML to express the CURP'
        'when the company is from a natural person.')
