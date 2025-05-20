
from odoo import fields, models

class AccountPayment(models.Model):
    _name = 'account.payment'
    _inherit = ['account.payment', 'mail.thread']

    l10n_mx_edi_original_string = fields.Text(
        'Original String', copy=False,
        help='Original String returned by the SAT, is used in PDF report.')

class AccountRegisterPayments(models.TransientModel):
    _inherit = 'account.register.payments'

    cfdi = fields.Binary(
        string='CFD-I',
        filters='*.xml'
    )
