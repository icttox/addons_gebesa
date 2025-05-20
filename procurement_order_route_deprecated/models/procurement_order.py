# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ProcurementOrder(models.Model):
    _inherit = "procurement.order"

    @api.model
    def _search_suitable_rule(self, procurement, domain):
        res = super(ProcurementOrder, self)._search_suitable_rule(
            procurement, domain)
        product_bom = False
        pull_obj = self.env['procurement.rule']
        for bom in procurement.product_id.bom_ids:
            if bom.product_id.id == procurement.product_id.id:
                product_bom = bom
        if product_bom and product_bom.routing_id:
            location = product_bom.routing_id.location_id
            new_res = pull_obj.search([(
                'location_src_id', '=', location.id)]).id
            if new_res in res:
                res = [new_res]
        return res
