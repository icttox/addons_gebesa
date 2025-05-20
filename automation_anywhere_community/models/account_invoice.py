# -*- coding: utf-8 -*-
# © <2019> <Samuel Barron>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models
from odoo.exceptions import UserError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def invoice_validate(self):
        for invoice in self:
            if invoice.type in ('in_invoice'):
                for line in invoice.invoice_line_ids:
                    if not line.product_id:
                        raise UserError((
                            'Al menos una linea no tiene producto asignado'))

        return super().invoice_validate()
