# Copyright 2020, Cesar Barron
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    @api.one
    @api.depends('picking_id', 'production_id')
    def _compute_extra_data(self):
        if self.picking_id:
            self.group_id = self.picking_id.group_id
            self.sale_id = self.picking_id.sale_id
            self.origin = self.picking_id.origin
        elif self.production_id:
            self.group_id = self.production_id.procurement_group_id
            self.sale_id = self.production_id.sale_id
            self.origin = self.production_id.origin
        else:
            self.group_id = False
            self.sale_id = False

    sale_id = fields.Many2one(
        'sale.order',
        string='Sale order',
        compute='_compute_extra_data',
        # store=True,
        readonly=True)

    group_id = fields.Many2one(
        'procurement.group',
        string='Grupo',
        compute='_compute_extra_data',
        readonly=True,
    )

    origin = fields.Char(
        string='Origin',
        compute='_compute_extra_data',
        readonly=True,
    )

    warehouse_id = fields.Many2one(
        'stock.warehouse',
        related='location_id.stock_warehouse_id',
        string='Almacen',
        readonly=True,
    )
