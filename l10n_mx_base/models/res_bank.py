# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class Bank(models.Model):
    _inherit = "res.bank"

    social_reason = fields.Char(
        help='Name by which a company is known collectively')

    code = fields.Char(help='Code indicated by SAT.')


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    clabe = fields.Char('CLABE',
                        help="Standardized banking cipher for Mexico. "
                        "More info wikipedia.org/wiki/CLABE")

    last_acc_number = fields.Char(
        'Last 4 digits',
        help="CFDI v3.2 request the last 4 digits of a bank account number"
        " for the field 'NumCtaPago' of xml.")
