# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, _


class ProductProductConsumption(models.TransientModel):
    _name = 'product.product.consumption.wizard'
    _description = 'descripcion pendiente'

    product_id = fields.Many2one(
        'product.product',
        string=_('Product'),
    )

    state = fields.Selection(
        [('in_production', _('Pending Order')),
         ('cancel', _('Cancelled Order')),
         ('done', _('Done Order'))],
        string=_('Status'),
        index=True,
    )
