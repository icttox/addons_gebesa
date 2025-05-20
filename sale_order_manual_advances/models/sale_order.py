# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    advance_ids = fields.One2many(
        'sale.order.manual.advances',
        'sale_id',
        string='Advance',
    )

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        for sale in self:
            if sale.advance_ids and (vals.get('advance_ids', False) or vals.get('amount_total', False)):
                total_advance = 0.0
                for advance in sale.advance_ids:
                    if advance.advance_id:
                        total_advance += advance.amount_advance
                if total_advance > self.amount_total:
                    raise UserError('La sumatoria de las facturas de anticipo es mayor que el monto total de este pedido')
        return res

    @api.multi
    def _prepare_invoice(self):
        invoice_vals = super()._prepare_invoice()
        advances = []
        for advance in self.advance_ids:
            advances.append((0, 0, {'advance_id': advance.advance_id.id, 'amount_advance': advance.amount_advance}))
        invoice_vals['advance_ids'] = advances
        return invoice_vals
