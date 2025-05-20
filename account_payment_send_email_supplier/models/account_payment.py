# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.multi
    def post(self):
        res = super().post()
        for payment in self:
            if payment.payment_type == 'outbound' and payment.partner_type == 'supplier':
                # pdf = payment.attachment_payment_pdf()
                # payment.send_email_payment(pdf=pdf)
                payment.send_email_payment()
        return res
