# -*- coding: utf-8 -*-

from odoo import models, fields


class AccountInvoice(models.Model):
    _inherit = 'account.move'

    terms = fields.Char(
        string='Terminos')

    freight = fields.Char(
        string='Flete')

    address = fields.Text(
        string='Dirección',)
