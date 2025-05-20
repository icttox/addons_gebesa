# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    address_issued_id = fields.Many2one(
        'res.partner', domain="[('type', '=', 'invoice')]",
        string='Address Issued',
        help='Used in environment multi-branch office, the invoices with this '
        'journal will use the partner address like issued address. If this '
        'value is empty, the issued address on invoice will take the value '
        'from company address.')

    auto_send_invoice = fields.Boolean(
        default=True, help='Whether the email will be sent with just validate'
        ' invoices (POS and/or B2C) or ask for an extra step opening the send'
        ' email wizard as normal before send the email (B2B)')


class AccountTax(models.Model):
    _inherit = 'account.tax'

    l10n_mx_edi_factor_type = fields.Selection(
        [('rate', 'Tasa'),
         ('quota', 'Cuota'),
         ('exempt', 'Exento')], 'Factor Type',
        help='Used to indicate the key of the type of factor that is applied '
        'to the tax base.')
