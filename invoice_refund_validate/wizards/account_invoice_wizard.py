# -*- coding: utf-8 -*-
# © 2017 Cesar Barron
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class AccountInvoiceWizard(models.TransientModel):
    _name = 'account.invoice.wizard'
    _description = 'descripcion pendiente'

    @api.multi
    def button_invoice_gebesa_wizard(self):
        invoice_obj = self.env['account.invoice']
        active_ids = self._context.get('active_ids', []) or []
        invoice_var = invoice_obj.browse(active_ids)
        for inv in invoice_var:
            inv.boton_privilegio = True
