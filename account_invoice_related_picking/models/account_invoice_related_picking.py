# -*- coding: utf-8 -*-
# © <2018> <Aldo Nerio>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models
# from odoo.exceptions import ValidationError


class AccountInvoiceRelatedPicking(models.Model):
    _inherit = 'stock.picking'

    account_invoice_id = fields.Many2one(
        'account.invoice',
        string='Factura correspondiente',
    )
