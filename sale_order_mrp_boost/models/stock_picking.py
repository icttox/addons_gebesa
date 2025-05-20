# Copyright 2024, Marco Esquivel
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class MrpProduction(models.Model):
    _inherit = 'stock.picking'

    segment_id = fields.Many2one(
        'mrp.segment',
        string='Segment',
    )
