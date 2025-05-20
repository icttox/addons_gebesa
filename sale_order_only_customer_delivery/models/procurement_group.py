# -*- coding: utf-8 -*-
# © <2019> <Samuel Barron>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models

class ProcurementGroup(models.Model):
    _inherit = 'procurement.group'

    @api.model
    def run(self, product_id, product_qty, product_uom,
            location_id, name, origin, values):
        location_usage = location_id.usage
        if values.get('group_id', False):
            only_cust_delivery = values['group_id'].sale_id.only_customer_delivery
            if only_cust_delivery is True and location_usage != 'customer':
                return True
        return super().run(
            product_id=product_id, product_qty=product_qty,
            product_uom=product_uom, location_id=location_id, name=name,
            origin=origin, values=values)
