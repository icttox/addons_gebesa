# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class MrpShipment(models.Model):
    _inherit = 'mrp.shipment'

    inv_rel_shipment_ids = fields.One2many(
        'inv.rel.shipment',
        'shipment_id',
        string='Shipment'
    )

    total_gasto_flete = fields.Monetary(
        string='Total Gasto Flete',
        compute='_compute_gasto_flete',
        currency_field='company_currency_id'
    )

    company_currency_id = fields.Many2one(
        'res.currency',
        related='company_id.currency_id',
        string="Company Currency",
    )

    company_id = fields.Many2one(
        'res.company',
        string='Company',
    )

    amount_total_mxn = fields.Float(
        string='Amount Total Mxn',
        compute='_compute_amount_total_mxn',
        store=True,
    )

    total_gasto_flete_mxn = fields.Float(
        string='Total Gasto Flete Mxn',
        compute='_compute_total_gasto_flete_mxn',
        store=True,
    )

    @api.multi
    @api.depends('inv_rel_shipment_ids')
    def _compute_gasto_flete(self):
        # Se hace la sumatoria de las facturas que se agregaron en los embarques.
        for ship in self:
            total_invoice = 0.0
            for rel in ship.inv_rel_shipment_ids:
                total_invoice += rel.total_inv
            ship.total_gasto_flete = total_invoice

    @api.multi
    @api.depends('line_ids')
    def _compute_amount_total_mxn(self):
        # Se hace la suma de las lineas del embarque del campo del total en pesos.
        for ship in self:
            total = 0
            for line in ship.line_ids:
                total += line.total_mxn
            ship.amount_total_mxn = total

    @api.multi
    @api.depends('inv_rel_shipment_ids')
    def _compute_total_gasto_flete_mxn(self):
        # Se hace la conversión a pesos dependiendo de la moneda que trae la compañia de la factura y de la moneda
        # de la factura que tiene el campo la sumatoria de las facturas.
        for ship in self:
            total = 0
            for rel in ship.inv_rel_shipment_ids:
                company_id = rel.invoice_id.company_id
                currency_id = company_id.currency_id
                if currency_id != rel.invoice_id.currency_id:
                    total += rel.invoice_id.currency_id._convert(
                        rel.total_inv, currency_id, company_id,
                        rel.invoice_id.date_invoice)
                else:
                    total += rel.total_inv
            ship.total_gasto_flete_mxn = total
