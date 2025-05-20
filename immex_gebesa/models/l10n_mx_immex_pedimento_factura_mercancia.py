# -*- coding: utf-8 -*-
# © <2021> <Samuel Barron, GEBESA>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class L10nMxImmexPedimentoFacturaMercancia(models.Model):
    _name = 'l10n.mx.immex.pedimento.factura.mercancia'
    _description = 'descripcion pendiente'

    immex_invoice_id = fields.Many2one(
        'l10n.mx.immex.pedimento.factura',
        string='Pedimento Factura',
    )
    pedimento_id = fields.Many2one(
        related='immex_invoice_id.pedimento_id',
        string='Pedimento',
    )
    invoice_id = fields.Many2one(
        'account.invoice',
        related='immex_invoice_id.invoice_id',
        string='Invoice',
    )
    descripcion = fields.Char(
        string='Descripcion',
    )
    clave_uom = fields.Char(
        string='Unidad de medida',
    )
    moneda = fields.Char(
        string='Moneda',
    )
    cantidad = fields.Float(
        string='Cantidad',
    )
    valor_unitario = fields.Float(
        string='Valor unitario',
    )
    valor_total = fields.Float(
        string='Valor total',
    )
    valor_dolares = fields.Float(
        string='Valor dolares',
    )
    partida_id = fields.Many2one(
        'l10n.mx.immex.partida',
        string='Partida',
    )
    invoice_line_id = fields.Many2one(
        'account.invoice.line',
        string='Linea de la Factura',
    )
