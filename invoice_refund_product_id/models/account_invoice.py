# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models

# mapping invoice type to refund type
TYPE2REFUND = {
    'out_invoice': 'out_refund',        # Customer Invoice
    'in_invoice': 'in_refund',          # Vendor Bill
    'out_refund': 'out_invoice',        # Customer Refund
    'in_refund': 'in_invoice',          # Vendor Refund
}


class AccountInvoiceRefund(models.Model):
    _inherit = 'account.invoice'

    def _refund_mode(self, values):
        """
            :param list(browse_record) lines: record to convert
            :return: list of command tuple for one2many line creation
                [(0, 0, dict of valueis), ...]
        """
        fiscal_position_obj = self.env['account.fiscal.position']
        product_obj = self.env['product.product']
        account_obj = self.env['account.account']

        product_id = self._context.get('product_id', False)
        type = self._context.get('type', False)
        amount = self._context.get('amount', False)

        partner_id = values.get('partner_id', False)
        fiscal_position_id = values.get('fiscal_position_id', False)

        # fis_pos = fiscal_position_id and fiscal_position_obj.browse(
        #    fiscal_position_id) or False

        res = product_obj.browse(product_id)
        account_id = res.property_account_expense_id.id
        uos_id = res.uom_id.id
        name = res.name_template
        if type in ('out_invoice', 'out_refund'):
            acc = res.property_account_income_id.id
            if not acc:
                acc = res.categ_id.property_account_income_categ_id.id
        else:
            acc = res.property_account_expense_id.id
            if not acc:
                acc = res.categ_id.property_account_income_categ_id.id
        acc = fiscal_position_obj.map_account(acc)

        if type in ('out_invoice', 'out_refund'):
            taxes = res.taxes_id and res.taxes_id or (
                acc and account_obj.browse(acc).tax_ids or False)
        else:
            taxes = res.supplier_taxes_id and res.supplier_taxes_id or (
                acc and account_obj.browse(acc).tax_ids or False)

        tax_id = []
        if taxes:
            for tax in taxes:
                if tax.included_id:
                    tax_id.append(tax.included_id.id)

        clean_lines = []
        clean_line = {}

        clean_line['account_id'] = account_id
        clean_line['name'] = name
        clean_line['product_id'] = product_id
        clean_line['account_analytic_id'] = values.get(
            'account_analytic_id', False)
        clean_line['company_id'] = values.get('company_id', False)
        clean_line['partner_id'] = partner_id
        clean_line['asset_category_id'] = False
        clean_line['discount'] = 0.0
        clean_line['invoice_id'] = False
        clean_line['origin'] = False
        clean_line['price_subtotal'] = amount
        clean_line['price_unit'] = amount
        clean_line['quantity'] = 1
        clean_line['trancking_id'] = False
        clean_line['move_id'] = False
        clean_line['uom_id'] = uos_id
        clean_line['invoice_line_tax_ids'] = [(6, 0, tax_id)]

        clean_lines.append((0, 0, clean_line))
        return clean_lines

    @api.model
    def _prepare_refund(self, invoice, date_invoice=None,
                        date=None, description=None, journal_id=None):
        """ Prepare the dict of values to create the new refund from the invoice.
            This method may be overridden to implement custom
            refund generation (making sure to call super() to establish
            a clean extension chain).

            :param record invoice: invoice to refund
            :param string date_invoice: refund creation date from the wizard
            :param integer date: force date from the wizard
            :param string description: description of the refund from
                the wizard
            :param integer journal_id: account.journal from the wizard
            :return: dict of value to create() the refund
        """
        values = {}
        for field in ['name', 'reference', 'comment', 'date_due', 'partner_id',
                      'company_id', 'account_id', 'currency_id',
                      'payment_term_id', 'user_id', 'fiscal_position_id',
                      'account_analytic_id']:
            if invoice._fields[field].type == 'many2one':
                values[field] = invoice[field].id
            else:
                values[field] = invoice[field] or False

        mode = self._context.get('mode', False)
        # origen_id = self._context.get('active_id', False)
        if mode == 'refund':
            values['invoice_line_ids'] = self._refund_mode(
                values)
        else:
            values['invoice_line_ids'] = self._refund_cleanup_lines(
                invoice.invoice_line_ids)

        tax_lines = filter(lambda l: l.manual, invoice.tax_line_ids)
        values['tax_line_ids'] = self._refund_cleanup_lines(tax_lines)

        if journal_id:
            journal = self.env['account.journal'].browse(journal_id)
        elif invoice['type'] == 'in_invoice':
            journal = self.env['account.journal'].search(
                [('type', '=', 'purchase')], limit=1)
        else:
            journal = self.env['account.journal'].search(
                [('type', '=', 'sale')], limit=1)
        values['journal_id'] = journal.id

        values['type'] = TYPE2REFUND[invoice['type']]
        values['date_invoice'] = date_invoice or fields.Date.context_today(
            invoice)
        values['state'] = 'draft'
        values['number'] = False
        values['origin'] = invoice.number

        if date:
            values['date'] = date
        if description:
            values['name'] = description
        return values
