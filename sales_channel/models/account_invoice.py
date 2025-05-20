# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    sales_channel_id = fields.Many2one(
        'sales.channel',
        string='Sales channel',
    )

    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        super()._onchange_partner_id()
        sales_channel_id = False
        payment_term_id = False
        if self.partner_id.sales_channel_id.id:
            sales_channel_id = self.partner_id.sales_channel_id.id
        self.sales_channel_id = sales_channel_id
        if self.partner_id.property_payment_term_id.id and self.partner_id.customer is True:
            payment_term_id = self.partner_id.property_payment_term_id.id
        if self.partner_id.property_supplier_payment_term_id.id and self.partner_id.supplier is True:
            payment_term_id = self.partner_id.property_supplier_payment_term_id.id
        self.payment_term_id = payment_term_id
