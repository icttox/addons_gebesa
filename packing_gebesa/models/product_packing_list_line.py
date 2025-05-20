# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, _, fields, models
from odoo.exceptions import ValidationError


class ProductPackingListLine(models.Model):
    _name = 'product.packing.list.line'
    _rec_name = 'description'
    _description = 'descripcion pendiente'

    packing_id = fields.Many2one(
        'product.packing.list',
        string='Packing',
        ondelete='cascade',
        index=True,
    )
    quantity = fields.Integer(
        string='Quantity',
    )
    description = fields.Text(
        string='Description',
    )
    unit_type_id = fields.Many2one(
        'logistic.unit.type',
        string='Unit Type',
    )

    @api.constrains('qty')
    def _check_quantity(self):
        for line in self:
            if line.quantity <= 0 or not line.quantity:
                raise ValidationError(_('Quantity must be greater than Zero'))
