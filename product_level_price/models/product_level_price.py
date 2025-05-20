# -*- coding: utf-8 -*-
# © 2017 Aldo Nerio
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductLevelPrice(models.Model):
    _name = 'product.level.price'
    _description = 'Product Price Level'
    _order = 'product_id asc'
    _rec_name = 'product_id'

    price_dis_a = fields.Float(
        string='Price Dis 00:',
        help='Price 00'
    )

    price_dis_b = fields.Float(
        string='Price Dis 00-01:',
        help='Price 00.01'
    )

    price_dis_c = fields.Float(
        string='Price Dis 01:',
        help='Price 01'
    )

    price_dis_d = fields.Float(
        string='Price Dis 02:',
        help='Price 02'
    )

    price_dis_e = fields.Float(
        string='Price Dis 03:',
        help='Price 03'
    )

    price_dis_f = fields.Float(
        string='Price Dis 04:',
        help='Price 04'
    )

    price_dis_g = fields.Float(
        string='Price Dis 05:',
        help='Price 05'
    )

    price_dis_h = fields.Float(
        string='Price Dis 06:',
        help='Price 06'
    )

    price_dis_i = fields.Float(
        string='Price Dis 07:',
        help='Price 07'
    )

    base_price = fields.Float(
        string='Base Price:',
        help='Base.Price'
    )

    price_dis_may = fields.Float(
        string='Base Dis-May 03:',
        help='Base Price 03'
    )

    price_may_a = fields.Float(
        string='Price May 00:',
        help='Price May'
    )

    price_may_b = fields.Float(
        string='Price May 01:',
        help='Price May'
    )

    price_may_c = fields.Float(
        string='Price May 02:',
        help='Price May'
    )

    price_may_d = fields.Float(
        string='Price May 03:',
        help='Price May'
    )

    price_may_e = fields.Float(
        string='Price May 04:',
        help='Price May'
    )

    price_may_f = fields.Float(
        string='Price May 05:',
        help='Price May'
    )

    price_may_g = fields.Float(
        string='Price May 06:',
        help='Price May'
    )

    price_may_h = fields.Float(
        string='Price May 07:',
        help='Price May'
    )

    standard_cost = fields.Float(
        string='Cost Std:',
        related='product_id.standard_price',
        readonly=True,
    )

    product_id = fields.Many2one(
        'product.product',
        string='Product:',
        help='Product',
        required=True,
    )

    mu_dist_may_id = fields.Many2one(
        'product.product.mu',
        string='M.U.Dist - May:',
        help='Product',
        required=True,
    )

    description = fields.Selection(
        [('metal', 'Metal-Madera'),
        ('silleria', 'Silleria-Cyber')],
        string='Description:',
        index=True,
        default='metal',
        required=True,
    )
