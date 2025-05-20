# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    warehouse_id = fields.Many2one(
        'stock.warehouse',
        # related='picking_type_id.warehouse_id',
        string='Warehouse',
        compute='_compute_warehouse_id',
        store=True,
    )

    @api.depends('picking_type_id')
    def _compute_warehouse_id(self):
        super()._onchange_picking_type_id()
        warehouse = self.picking_type_id.warehouse_id
        self.warehouse_id = warehouse.id
