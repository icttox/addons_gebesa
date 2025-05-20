# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    purchase_ids = fields.Many2many(
        'purchase.order',
        string='Purchase Order',
    )

    @api.onchange('purchase_id')
    def _onchange_purchase_order(self):
        purchase_ids = []
        if self.purchase_id:
            purchase_ids.append(self.purchase_id.id)
        for purchase in self.purchase_ids:
            purchase_ids.append(purchase.id)
        self.purchase_ids = purchase_ids
