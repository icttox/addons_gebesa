# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleOrderManualAdvances(models.Model):
    _name = 'sale.order.manual.advances'
    _description = 'descripcion pendiente'

    sale_id = fields.Many2one(
        'sale.order',
        string='Sale Order',
    )
    advance_id = fields.Many2one(
        'account.invoice',
        string='Advance',
    )
    amount_advance = fields.Float(
        string='Amount Advance',
    )

    @api.onchange('advance_id')
    def _onchange_advance_id(self):
        advance = self.advance_id
        if advance:
            if advance.amount_residual_advance >= self.sale_id.amount_total:
                self.amount_advance = self.sale_id.amount_total
            else:
                self.amount_advance = advance.amount_residual_advance

        return
