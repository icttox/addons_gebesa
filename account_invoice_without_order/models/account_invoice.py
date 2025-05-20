# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models
from odoo.exceptions import UserError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def invoice_validate(self):
        for invoice in self:
            if invoice.type in ('out_invoice', 'out_refund'):
                if not invoice.sale_id and not self.env.user.has_group(
                        'account_invoice_without_order.group_account_invoice_without_order'):
                    raise UserError(_('You do not have privileges to validate '
                                      'invoices without order'))
        return super().invoice_validate()

    @api.model
    def create(self, vals_list):
        invoice_type = self._context.get('type', 'out_invoice')
        if invoice_type in ('out_invoice', 'out_refund'):
            if 'sale_id' not in vals_list.keys() or vals_list['sale_id'] is False:
                if not self.env.user.has_group(
                        'account_invoice_without_order.group_account_invoice_without_order'):
                    raise UserError(_('You do not have privileges to create '
                                      'invoices without order'))
        return super().create(vals_list)

    @api.multi
    def write(self, vals):
        if self.type in ('out_invoice', 'out_refund'):
            if ('sale_id' not in vals.keys() or vals['sale_id'] is False) and not self.sale_id:
                if not self.env.user.has_group(
                        'account_invoice_without_order.group_account_invoice_without_order'):
                    raise UserError(_('You do not have privileges to update '
                                      'invoices without order'))
        return super().write(vals)

    @api.multi
    def action_invoice_open(self):
        for invoice in self:
            if invoice.type in 'in_refund':
                num_nc = self.env['account.invoice'].search_count([
                    ('reference', 'like', invoice.reference),
                    ('partner_id', '=', invoice.partner_id.id),
                    ('type', '=', 'in_refund')])
                invoice.reference = invoice.reference + '-' + str(num_nc)
            if invoice.type == 'in_invoice' and invoice.purchase_ids:
                if invoice.currency_id != invoice.purchase_ids.currency_id:
                    raise UserError(_('Need same currency.'))
        return super().action_invoice_open()
