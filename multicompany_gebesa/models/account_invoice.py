# Copyright 2022, Cesar Barron
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, models
from odoo.exceptions import UserError


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    @api.multi
    def invoice_validate(self):
        """ Validated invoice generate cross invoice base on company rules """
        for invoice in self:
            # do not consider invoices that have already been auto-generated, nor the invoices that were already validated in the past
            company = self.env['res.company']._company_from_partner(invoice.partner_id.id)
            if company and company.sincronize_invoices_too and not invoice.auto_generated:
                if invoice.type == 'out_invoice':
                    invoice.inter_company_create_invoice(company, 'in_invoice', 'purchase')
                elif invoice.type == 'out_refund':
                    invoice.inter_company_create_invoice(company, 'in_refund', 'purchase')
                elif invoice.type == 'in_invoice':
                    invoice.inter_company_create_invoice(company, 'out_invoice', 'sale')
                elif invoice.type == 'in_refund':
                    invoice.inter_company_create_invoice(company, 'out_refund', 'sale')

            if invoice.company_id.country_id != self.env.ref('base.mx'):
                continue
            if not self.env.user.has_group('multicompany_gebesa.validate_without_taxes'):
                for line in invoice.invoice_line_ids:
                    if not line.invoice_line_tax_ids:
                        raise UserError('Al menos una linea no tiene impuestos')
        return super(AccountInvoice, self).invoice_validate()
