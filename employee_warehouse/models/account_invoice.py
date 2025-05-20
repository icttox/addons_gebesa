# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def invoice_validate(self):
        for invoice in self:
            if invoice.account_analytic_id.warehouse_id:
                warehouse = invoice.account_analytic_id.warehouse_id
                employee = self.env['hr.employee'].sudo().search(
                    [('user_id', '=', self._uid)])
                if warehouse not in employee.warehouse_ids:
                    raise ValidationError(_("You do not have privileges to validate \
                                          in this warehouse."))
            for line in invoice.invoice_line_ids:
                if line.quantity == 0:
                    raise ValidationError(_('Al menos una de las lineas de la \
                                            Factura tiene Cantidad cero!'
                                            '\n Por favor asegurese \
                                            que todas las lineas tengan capturada la Cantidad.'))
            if invoice.type == 'in_invoice' and not invoice.reference:
                raise ValidationError(_("Usted no puede validar esta Factura sin \
                                          el número de Referencia del Proveedor."))
        return super().invoice_validate()
