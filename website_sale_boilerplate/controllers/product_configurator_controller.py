# -*- coding: utf-8 -*-
# Copyright 2022, Samuel Barron
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.sale.controllers.product_configurator import ProductConfiguratorController
from odoo.http import request
from odoo import http


class ProductConfiguratorVisibility(ProductConfiguratorController):

    @http.route(['/product_configurator/get_combination_info'], type='json', auth="user", methods=['POST'])
    def get_combination_info(self, product_template_id, product_id, combination, add_qty, pricelist_id, **kw):
        result = super(ProductConfiguratorVisibility, self).get_combination_info(product_template_id, product_id, combination, add_qty, pricelist_id, **kw)

        if result['product_id']:
            visible_product = request.env['product.product'].browse(result['product_id'])

            if visible_product and not visible_product.show_web_portal:
                result['is_combination_possible'] = False

        return result
