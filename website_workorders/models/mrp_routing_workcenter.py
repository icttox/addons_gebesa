# Copyright 2024, Samuel Barron
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models


class MrpRoutingWorkcenter(models.Model):
    _name = 'mrp.routing.workcenter'
    _inherit = 'mrp.routing.workcenter'

    def get_products_production_load(self, workcenter_id):
        routing_ids = self.sudo().search([
            ('workcenter_id', '=', workcenter_id)]).mapped('routing_id').ids
        products = self.env['mrp.bom'].sudo().search([
            ('routing_id', 'in', routing_ids)]).mapped('product_id')

        product_dict = []
        for product in products.with_context(lang='es_MX'):
            product_dict.append({
                'id': product.id,
                'name': '[' + product.default_code + '] ' + product.name
            })
        return product_dict
