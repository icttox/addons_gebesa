# Copyright 2024, Marco Esquivel
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models
from odoo.addons import decimal_precision as dp


class AttendanceReportsWizard(models.TransientModel):
    _name = 'production.mo.grouped'
    _description = 'Wizard para agrupar Mo dependiendo del segmento y la ubicacion'

    product_id = fields.Many2one(
        'product.product',
        string='Product',
    )

    quantity_pending = fields.Float(
        string='Quantity pending',
        default=0.0,
        digits=dp.get_precision('Product Unit of Measure'),
    )

    quantity = fields.Float(
        string='Quantity',
        default=0.0,
        digits=dp.get_precision('Product Unit of Measure'),
    )

    production_segment_id = fields.Many2one(
        'mrp.production.segment.grouped',
        string='Production',
    )

    delivered_quantity = fields.Float(
        string='Delivered quantity',
        default=0.0,
        digits=dp.get_precision('Product Unit of Measure'),
    )

    total_quantity = fields.Float(
        string='Total quantity',
        default=0.0,
        digits=dp.get_precision('Product Unit of Measure'),
    )
