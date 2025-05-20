
from odoo import models, fields, api


class InvRelSo(models.Model):
    _name = 'inv.rel.so'
    _description = 'descripcion pendiente'

    invoice_id = fields.Many2one(
        'account.invoice',
        string='Invoice',
    )

    order_id = fields.Many2one(
        'sale.order',
        string='Order',
    )

    currency_inv_id = fields.Many2one(
        related='invoice_id.currency_id',
        string='Currency Invoice',
    )

    total_inv = fields.Monetary(
        string='Total Invoice',
        related='invoice_id.amount_total',
        currency_field='currency_inv_id'
    )

    currency_order_id = fields.Many2one(
        related='order_id.currency_id',
        string="Currency Order",
    )

    total_so = fields.Monetary(
        string='Total Sale Order',
        related='order_id.amount_total',
        currency_field='currency_order_id'
    )

    gasto_pro_flete = fields.Float(
        string="Gasto Prorrateo Flete",
        compute='_compute_pro_flete',
        store=True,
    )

    @api.multi
    @api.depends('total_so', 'invoice_id.total_sale', 'invoice_id.amount_total')
    def _compute_pro_flete(self):
        #Se hace el prorrateo del gasto de flete en base a la operacion del total de la order de venta que se
        #agrega a la factura entre el total de la sumatoria de los pedidos agregados en la factura por
        #el total de la factura.
        for rel_so in self:
            if rel_so.invoice_id.total_sale != 0.0:
                rel_so.gasto_pro_flete = (rel_so.total_so / rel_so.invoice_id.total_sale) * rel_so.invoice_id.amount_total
            else:
                rel_so.gasto_pro_flete = 0.0
