# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, models, tools, api
import odoo.addons.decimal_precision as dp


class ProductAttributeValue(models.Model):
    _inherit = 'product.attribute.value'
    _name = 'product.attribute.value'

    active = fields.Boolean(
        string='Active',
        default=True,
    )

    factor = fields.Float(
        string='Factor',
        digits=dp.get_precision('Account')
    )

    # image = fields.Binary(
    #    string='Image')

    isometric = fields.Binary(
        string="Isometric image",
        attachment=True,
    )

    isometric_medium = fields.Binary(
        string="Medium-sized isometric image",
        attachment=True,
    )

    isometric_small = fields.Binary(
        string="Small-sized isometric image",
        attachment=True,
    )

    @api.model
    def create(self, vals):
        tools.image_resize_images(vals=vals, big_name='isometric',
                                  medium_name='isometric_medium',
                                  small_name='isometric_small')
        return super(ProductAttributeValue, self).create(vals)

    @api.multi
    def write(self, vals):
        tools.image_resize_images(vals=vals, big_name='isometric',
                                  medium_name='isometric_medium',
                                  small_name='isometric_small')
        return super(ProductAttributeValue, self).write(vals)


class ProductAttribute(models.Model):
    _inherit = 'product.attribute'
    _name = 'product.attribute'

    active = fields.Boolean(
        string='Active',
        default=True,
    )
