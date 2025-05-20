# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, tools


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    pricelist = fields.Boolean(
        string='Is price list',
        help='the product is displayed in the price list',
    )
    note_pricelist = fields.Text(
        string='Note price list',
    )
    length = fields.Integer(
        string='Length',
        help='length in cm',
    )
    width = fields.Integer(
        string='Width',
        help='width in cm',
    )
    height = fields.Integer(
        string='Height',
        help='height in cm',
    )
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
    product_mix_id = fields.Many2one(
        'product.template',
        string='Product mixta',
    )
    vias = fields.Selection(
        [(2, 2),
         (3, 3),
         (4, 4)],
        string="Vias",
    )
    acabados_html = fields.Html(
        string="Finished Html"
    )
    notas_html = fields.Html(
        string="Notes Html"
    )
    composiciones_html = fields.Html(
        string="Compositions Html"
    )
    pricelist_categ_id = fields.Many2one(
        'product.pricelist.category',
        string='Categoría de lista de precios',
    )

    @api.model
    def create(self, vals_list):
        tools.image_resize_images(vals=vals_list, big_name='isometric',
                                  medium_name='isometric_medium',
                                  small_name='isometric_small')
        return super().create(vals_list)

    @api.multi
    def write(self, vals):
        tools.image_resize_images(vals=vals, big_name='isometric',
                                  medium_name='isometric_medium',
                                  small_name='isometric_small')
        return super().write(vals)


class ProductLine(models.Model):
    _inherit = 'product.line'

    acabados_html = fields.Html(
        string='Finished Html',
    )

    notas_html = fields.Html(
        string='Notes Html',
    )

    composiciones_html = fields.Html(
        string='Compositions Html',
    )

    portada_html = fields.Html(
        string='Portada',
    )


class ProductAttributeValue(models.Model):
    _inherit = 'product.attribute.value'

    number = fields.Char(
        string='Number',
        compute='_compute_number'
    )

    @api.depends('attribute_code')
    def _compute_number(self):
        for record in self:
            record.number = "".join(
                [x for x in record.attribute_code if x.isdigit()])
