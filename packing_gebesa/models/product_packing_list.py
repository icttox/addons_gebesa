# -*- coding: utf-8 -*-
# © 2018 Aldo Nerio
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, _, fields, models
from odoo.exceptions import ValidationError


class ProductPackingList(models.Model):
    _name = 'product.packing.list'
    _rec_name = 'name'
    _description = 'descripcion pendiente'

    name = fields.Char(
        string='Name',
        compute='_compute_name',
        store=True,
    )
    description = fields.Text(
        string='Description',
    )
    product_tmpl_id = fields.Many2one(
        'product.template',
        string='Product Template',
    )
    type = fields.Selection(
        [('standard', 'Standard'),
         ('exeption', 'Exeption')],
        string='Type',
        default='standard',
    )
    active = fields.Boolean(
        string='Active',
        default=True
    )
    qty = fields.Integer(
        string='Quantity Packing',
    )
    packing_line_ids = fields.One2many(
        'product.packing.list.line',
        'packing_id',
        string='Packing Details',
        copy=True,
    )

    @api.constrains('product_tmpl_id', 'type', 'active')
    def _check_packing_list_active(self):
        packing_obj = self.env['product.packing.list']
        bom_obj = self.env['mrp.bom']
        for packing in self:
            packing_var = packing_obj.search([
                ('product_tmpl_id', '=', packing.product_tmpl_id.id),
                ('active', '=', True),
                ('type', '=', 'standard')])
            bom_var = bom_obj.search([
                ('product_tmpl_id', '=', packing.product_tmpl_id.id),
                ('active', '=', True),
                ('type', '=', 'phantom')])
            if packing.type == 'standard':
                if len(packing_var) > 1:
                    raise ValidationError(_(
                        'Only one standard packing must exist by Product'))
                if bom_var:
                    raise ValidationError(_(
                        'A Kit Product cannot have a Standard Packing, Its \
                        Standard Packing are the components'))
            else:
                if not bom_var and not packing_var:
                    raise ValidationError(_(
                        'In order to create a Exception Packing, you must to \
                        create a Standard Packing first.'))

    @api.constrains('qty', 'packing_line_ids')
    def _check_packing_quantity(self):
        for packing in self:
            if packing.qty > 0:
                if packing.packing_line_ids:
                    raise ValidationError(_(
                        'The packing detail is only allowed when tha max \
                        quantity is 0'))
            elif not packing.packing_line_ids:
                raise ValidationError(_(
                    'If the max quantity is zero, you have to specify the \
                    packing detail'))
            else:
                for line in packing.packing_line_ids:
                    if line.quantity <= 0 or not line.quantity:
                        raise ValidationError(_(
                            'The detail quantity must be greater than zero'))

    @api.depends('description', 'type')
    def _compute_name(self):
        for rec in self:
            if rec.description:
                rec.name = rec.description + '-' + rec.type
