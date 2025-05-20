# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class L10nMxImmexPartidaDescargue(models.Model):
    _name = 'l10n.mx.immex.partida.descargue'
    _description = 'descripcion pendiente'

    invoice_id = fields.Many2one(
        'account.invoice',
        string='Invoice',
        ondelete='cascade',
    )
    invoice_line_id = fields.Many2one(
        'account.invoice.line',
        string='Invoice line',
        ondelete='cascade',
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
    )
    partida_type_id = fields.Many2one(
        'l10n.mx.immex.partida.type',
        string='Immex Clasificación',
    )
    quantity = fields.Float(
        string='Quantity',
    )
    qty_pending = fields.Float(
        string='Quantity pending',
    )
    line_ids = fields.One2many(
        'l10n.mx.immex.partida.descargue.line',
        'descargue_id',
        string='Line',
    )


class L10nMxImmexPartidaDescargueLine(models.Model):
    _name = 'l10n.mx.immex.partida.descargue.line'
    _description = 'descripcion pendiente'

    descargue_id = fields.Many2one(
        'l10n.mx.immex.partida.descargue',
        string='Descargue',
        ondelete='cascade',
    )
    partida_id = fields.Many2one(
        'l10n.mx.immex.partida',
        string='Partida',
    )
    quantity = fields.Float(
        string='Quantity',
    )
    invoice_id = fields.Many2one(
        'account.invoice',
        related='descargue_id.invoice_id',
        string='Invoice',
    )
    invoice_line_id = fields.Many2one(
        'account.invoice.line',
        related='descargue_id.invoice_line_id',
        string='Invoice Line',
    )
    product_id = fields.Many2one(
        'product.product',
        related='descargue_id.product_id',
        string='Product',
    )
