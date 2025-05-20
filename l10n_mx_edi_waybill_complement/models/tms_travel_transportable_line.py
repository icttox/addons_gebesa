# -*- coding: utf-8 -*-

from odoo import models, fields


class TmsTravelTransportableLine(models.Model):
    _inherit = 'tms.travel.transportable.line'

    delivery_id = fields.Many2one(
        'tms.travel.delivery',
        string='Travel Delivery',
    )

    weight = fields.Float(
        string="Unit Weight",
        digits=(16, 3),
    )

    gross_weight = fields.Float(
        string='Gross Unit Weight',
        digits=(16, 3),
    )

    pedimento_ids = fields.One2many(
        'tms.travel.transportable.line.pedimento',
        'transportable_line_id',
        string='Pedimentos',
    )

    _sql_constraints = [
        ('transportable_delivery_uniq', 'unique(transportable_id,delivery_id)', 'Combination Transportable - Delivery must be unique!'),
    ]


class TmsTravelTransportableLinePedimento(models.Model):
    _name = 'tms.travel.transportable.line.pedimento'
    _description = 'descripcion pendiente'

    transportable_line_id = fields.Many2one(
        'tms.travel.transportable.line',
        string='Load',
    )
    document_type = fields.Char(
        string='Tipo Documento',
    )
    name = fields.Char(
        string='Pedimento',
    )
    folio = fields.Char(
        string='Folio del Documento Aduanero',
    )
    importer_rfc = fields.Char(
        string='RFC del Importador',
    )
