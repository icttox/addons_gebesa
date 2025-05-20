# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def invoice_validate(self):
        template_obj = self.env['product.product']
        for lines in self.invoice_line_ids:
            template_var = template_obj.search([('id', '=', lines.product_id.id)])
            if template_var.type == 'cotiza':
                raise ValidationError(_('This product is type quotation: %s,  not cant Validate this Invoice') % (template_var.name))
        return super(AccountInvoice, self).invoice_validate()
