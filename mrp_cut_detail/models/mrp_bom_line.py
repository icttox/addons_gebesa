# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    bom_line_detail_ids = fields.One2many(
        'mrp.bom.line.detail',
        'bom_line_id',
        string='BoM Line Details',
        copy=True,
    )

    @api.multi
    def write(self, values):
        # bom_obj = self.env['mrp.bom']
        # product_obj = self.env['product.product']
        # if 'bom_id' in values.keys():
        #     bom = bom_obj.browse(values['bom_id'])
        # else:
        #     bom = self.bom_id
        # if 'product_id' in values.keys():
        #     producto = product_obj.browse(values['product_id'])
            # if producto.id == bom.product_id.id:
            #     raise UserError(_('One product cannot be detail of itself'))
            # for line in bom.bom_line_ids:
            #     if line.product_id.id == producto.id:
            #         raise UserError(_('This product is already in this Bom'))
        res = super(MrpBomLine, self).write(values)
        if 'product_id' in values.keys():
            details = self.mapped('bom_line_detail_ids')
            details.create_line_attribute()
        return res

    @api.multi
    def create(self, vals):
        # bom_obj = self.env['mrp.bom']
        # product_obj = self.env['product.product']
        # producto = product_obj.browse(vals['product_id'])
        # bom = bom_obj.browse(vals['bom_id'])
        # if producto.id == bom.product_id.id:
        #     raise UserError(_('One product cannot be detail of itself'))
        # for line in bom.bom_line_ids:
        #     if line.product_id.id == producto.id:
        #         raise UserError(_('This product is already in this Bom'))
        return super(MrpBomLine, self).create(vals)
