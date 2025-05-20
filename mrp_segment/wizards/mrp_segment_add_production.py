# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class MrpSegmentAddProduction(models.TransientModel):
    _name = 'mrp.segment.add.production'
    _description = 'descripcion pendiente'

    location_id = fields.Many2one(
        'stock.location',
        string='Segment location',
    )
    production_ids = fields.Many2many(
        'mrp.production',
        string=('Production'),
    )

    @api.multi
    def add_production(self):
        segment_obj = self.env['mrp.segment']
        segment_line_obj = self.env['mrp.segment.line']
        active_ids = self._context.get('active_ids', []) or []
        active_model = self._context.get('active_model') or False
        if active_model != 'mrp.segment':
            raise UserError(_('No puedes agregar MO desde aqui, '
                              'favor de navegar hasta la lista de segmentos, '
                              'seleccionar el segmento deseado y agregar la MO'))
        segment = segment_obj.browse(active_ids)
        for produ in self.production_ids:
            segment_line_obj.create({
                'segment_id': segment.id,
                'mrp_production_id': produ.id,
                'product_id': produ.product_id.id,
                'sale_name': produ.origin,
                'manufacture_qty': produ.product_qty,
                'product_qty': produ.product_qty,
                'quantity': 0,
                'standard_cost': produ.product_id.standard_price,
            })
