# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    boton_privilegio = fields.Boolean(
        string='Aprobar',
        track_visibility=True,
    )

    order_ref_id = fields.Many2one(
        'sale.order',
        string='Order Ref',
    )

    @api.multi
    def button_invoice_gebesa(self):
        self.boton_privilegio = True

    @api.multi
    def invoice_validate(self):
        res = {}
        if self.type == 'out_refund' and not self.boton_privilegio:
            raise ValidationError(_("This note credit not is validated"))
        res = super(AccountInvoice, self).invoice_validate()
        return res
