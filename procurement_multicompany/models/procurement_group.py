# -*- coding: utf-8 -*-
# © 2017 Cesar Barron
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class ProcurementGroup(models.Model):
    _inherit = 'procurement.group'

    def _get_orderpoint_domain(self, company_id=False):
        domain = super(ProcurementGroup, self)._get_orderpoint_domain(
            company_id=company_id)
        order_id = self._context.get('force_sale_order', False)
        if order_id:
            product_ids = order_id.order_line.mapped('product_id').mapped('id')
            domain += [('product_id.id', 'in', product_ids)]
        return domain
