# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    lines = fields.Char(
        string='Lines',
        compute='_compute_lines'
    )
    groups = fields.Char(
        'Groups',
        compute='_compute_lines'
    )
    familys = fields.Char(
        'Family',
        compute='_compute_lines'
    )
    volume = fields.Float(
        'Volumen',
        compute='_compute_lines'
    )
    weight = fields.Float(
        'Weight',
        compute='_compute_lines'
    )
    delay = fields.Integer(
        'Delay',
        compute='_compute_delay'
    )
    amount_pending = fields.Float(
        'Amount pending',
        store=True,
        compute='_compute_amount_pending'
    )
    standard_cost_pending = fields.Float(
        'Standard cost pending',
        compute='_compute_standard_cost_pending',
        store=False,
    )

    @api.depends('order_line.pending_qty', 'order_line.net_sale')
    def _compute_amount_pending(self):
        for sale in self:
            sale.amount_pending = 0
            for line in sale.order_line:
                if line.product_uom_qty > 0:
                    sale.amount_pending += line.pending_qty * (line.net_sale / line.product_uom_qty)

    @api.depends('order_line.standard_cost',
                 'order_line.pending_qty',
                 'order_line.product_uom_qty')
    def _compute_standard_cost_pending(self):
        for sale in self:
            sale.standard_cost_pending = 0
            for line in sale.order_line:
                if line.product_uom_qty > 0:
                    sale.standard_cost_pending += line.pending_qty *\
                        (line.standard_cost / line.product_uom_qty)

    @api.depends('date_order')
    def _compute_delay(self):
        for sale in self:
            sale.delay = (fields.Date.today() - sale.date_order.date()).days

    @api.depends('order_line')
    def _compute_lines(self):
        for sale in self:
            lin = grou = fam = ''
            volume = weight = 0
            lines = groups = family = []
            for order_line in sale.order_line:
                product = order_line.product_id
                volume += (order_line.product_uom_qty * product.volume)
                weight += (order_line.product_uom_qty * product.weight)
                if product.family_id.name:
                    if product.family_id.name not in family:
                        family.append(product.family_id.name)
                        fam = fam + ' ' + product.family_id.name + ','
                if product.group_id.name:
                    if product.group_id.name not in groups:
                        groups.append(product.group_id.name)
                        grou = grou + ' ' + product.group_id.name + ','
                if product.line_id.name:
                    if product.line_id.name not in lines:
                        lines.append(product.line_id.name)
                        lin = lin + ' ' + product.line_id.name + ','
            sale.lines = lin[1:-1]
            sale.groups = grou[1:-1]
            sale.familys = fam[1:-1]
            sale.volume = volume
            sale.weight = weight
