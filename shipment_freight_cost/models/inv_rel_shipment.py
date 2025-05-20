
from odoo import models, fields, _


class InvRelShipment(models.Model):
    _name = 'inv.rel.shipment'
    _description = 'descripcion pendiente'

    invoice_id = fields.Many2one(
        'account.invoice',
        string='Invoice',
    )

    shipment_id = fields.Many2one(
        'mrp.shipment',
        string='Shipment',
    )

    currency_id = fields.Many2one(
        related='invoice_id.currency_id',
        string='Currency',
    )

    total_inv = fields.Monetary(
        string='Total Invoice',
        related='invoice_id.amount_total',
    )

    _sql_constraints = [
        ('invoice_id_unique', 'unique(invoice_id)', _('The invoice must be unique.')),
    ]
