# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    inv_rel_so_ids = fields.One2many(
        'inv.rel.so',
        'invoice_id',
        string='Order',
    )

    inv_rel_shipment_ids = fields.One2many(
        'inv.rel.shipment',
        'invoice_id',
        string='Shipment',
    )

    total_sale = fields.Float(
        string="Total Sale",
        compute='_compute_total_sale',
        store=True,
    )

    @api.multi
    @api.depends('inv_rel_so_ids')
    def _compute_total_sale(self):
        # Es la sumatoria del total de los pedidos de venta.
        for inv in self:
            total = 0.0
            for rel in inv.inv_rel_so_ids:
                total += rel.total_so
            inv.total_sale = total
