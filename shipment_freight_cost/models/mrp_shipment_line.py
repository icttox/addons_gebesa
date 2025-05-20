# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class MrpShipmentLine(models.Model):
    _inherit = 'mrp.shipment.line'

    gasto_pro_flete = fields.Float(
        string="Gasto Prorrateo Flete",
        compute='_compute_pro_flete',
    )

    total_mxn = fields.Float(
        string="Total Mxn",
        compute='_compute_total_mxn',
        store=True,
    )

    gasto_pro_flete_mxn = fields.Float(
        string="Gasto Prorrateo Flete MXN",
        compute='_compute_pro_flete_mxn',
        store=True,
    )

    @api.multi
    @api.depends('gasto_pro_flete_mxn')
    def _compute_pro_flete(self):
        #Del la moneda de la compañia de las lineas del embarque del pedido y de la moneda del embarque del pedido
        #se hace una validación para hacer la conversión a pesos del campo del prorrateo ahora en pesos.
        for ship_line in self:
            total = ship_line.gasto_pro_flete_mxn
            company_id = ship_line.sale_order_id.company_id
            currency_id = company_id.currency_id
            if currency_id != ship_line.sale_order_id.currency_id:
                total = currency_id._convert(total, ship_line.sale_order_id.currency_id, company_id, ship_line.sale_order_id.date_validator)
            ship_line.gasto_pro_flete = total

    @api.multi
    @api.depends('total_mxn', 'shipment_id.amount_total_mxn', 'shipment_id.total_gasto_flete_mxn')
    def _compute_pro_flete_mxn(self):
        #En el prorrateo se asigna a cada linea un valor apatir de la operación del total de la linea del embarque en pesos de
        #entre el total del embarque, ese resultado por el casmpo que tiene el total de las facturas en pesos. Tambien si un valor se
        #divide entre 0, marca excepción.
        for ship_line in self:
            if ship_line.shipment_id.amount_total_mxn != 0.0:
                ship_line.gasto_pro_flete_mxn = (ship_line.total_mxn / ship_line.shipment_id.amount_total_mxn) * ship_line.shipment_id.total_gasto_flete_mxn
            else:
                ship_line.gasto_pro_flete_mxn = 0.0

    @api.multi
    @api.depends('quantity_shipped')
    def _compute_total_mxn(self):
        #De la operación del total de la linea de la order de venta entre la cantidad de la linea del pedido
        #por la cantidad embarcada de la linea del embarque. Este total, se hara su conversión que dependiendo de
        #la moneda que traia la compañia del pedido del la linea del embarque y de la moneda que tenga el
        #pedido de las lineas del embarque.
        for line in self:
            if line.order_line_id.product_uom_qty != 0.0:
                total = (line.order_line_id.price_total / line.order_line_id.product_uom_qty) * line.quantity_shipped
                company_id = line.sale_order_id.company_id
                currency_id = company_id.currency_id
                if currency_id != line.sale_order_id.currency_id:
                    total = line.sale_order_id.currency_id._convert(total, currency_id, company_id, line.sale_order_id.date_validator)
                line.total_mxn = total
            else:
                line.total_mxn = 0.0
