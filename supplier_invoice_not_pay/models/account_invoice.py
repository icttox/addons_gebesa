# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api, fields, _


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    not_pay = fields.Boolean(
        string='Not Pay Invoice',
        default=False,
        copy=False,
        track_visibility='onchange',
    )

    notpay_text = fields.Char(
        string='Pay Invoice',
        compute='_compute_not_pay',
        track_visibility='onchange',
    )

    @api.depends('not_pay')
    def _compute_not_pay(self):
        for rec in self:
            yes = _('Pay the Bill')
            no = _('Not Pay the Bill')
            if rec.not_pay is False:
                rec.notpay_text = yes
            else:
                rec.notpay_text = no
        return True
