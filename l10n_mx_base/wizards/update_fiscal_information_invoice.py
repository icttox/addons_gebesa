# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class UpdateInvoiceFiscalInformation(models.TransientModel):
    _name = "update.invoice.fiscal.information"

    date_from = fields.Date(
        help='Initial date to get invoices to update fiscal information.')
    date_to = fields.Date(
        help='Final date to get invoices to update fiscal information.')

    @api.model
    def default_get(self, fieldnames):
        """This function load by default in wizard the period to search
        invoices to update fiscal information"""
        res = super(
            UpdateInvoiceFiscalInformation, self).default_get(fieldnames)
        date = fields.Datetime.context_timestamp(
            self, fields.Datetime.from_string(
                fields.Datetime.now()))
        res.update({
            'date_from': date.replace(day=1).strftime('%Y-%m-%d'),
            'date_to': date.strftime('%Y-%m-%d'),
        })
        return res

    @api.multi
    def execute_update_invoice(self):
        invoice_obj = self.env['account.invoice']
        invoice_ids = self._context.get('active_ids', [])
        date = fields.Datetime.context_timestamp(
            self, fields.Datetime.from_string(
                fields.Datetime.now()))
        date_from = self.date_from or date.replace(day=1).strftime('%Y-%m-%d')
        date_to = self.date_to or date.strftime('%Y-%m-%d')
        invoice_obj.browse(invoice_ids).update_cfdi_status_sat(
            date_from, date_to
        )
        return True

    @api.model
    def execute_cron(self):
        self.execute_update_invoice()
        return True
