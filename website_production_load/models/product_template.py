# Copyright 2023, Cesar Barron
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    workcenter_id = fields.Many2one(
        'mrp.workcenter',
        string='Centro de producción',
    )
