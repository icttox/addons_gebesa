# Copyright 2022, Samuel Barron
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def get_product_from_sale(self, sale):
        dict_product = []
        sale_id = self.env['sale.order'].sudo().search([
            ('name', '=', sale)])
        poductions = self.sudo().search([('sale_id', '=', sale_id.id)])
        if not poductions:
            poductions = self.sudo().search([
                ('sale_order_ids', 'in', sale_id.ids)])
        products = poductions.mapped('product_id')

        for product in products.with_context(lang='es_MX'):
            dict_product.append([product.id, product.display_name])

        return dict_product
