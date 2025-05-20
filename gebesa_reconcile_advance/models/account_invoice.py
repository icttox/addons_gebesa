# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.exceptions import UserError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    reconcile_advance_ids = fields.Many2many(
        'gebesa.reconcile.advance',
        string='Conciliaciones de anticipo',
        copy=False,
    )

    @api.multi
    def action_cancel(self):
        for inv in self:
            if inv.reconcile_advance_ids:
                raise UserError(
                    "La factura %s tiene anticipos conciliados" % inv.number)
        return super().action_cancel()
