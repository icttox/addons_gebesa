# Copyright 2020, Cesar Barron
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class StockRule(models.Model):
    _inherit = 'stock.rule'

    @api.multi
    def _run_buy(self, product_id, product_qty, product_uom, location_id, name, origin, values):
        company_id = location_id.company_id
        # if company_id.is_manufacturer and 'orderpoint_id' not in values:
        if company_id.is_manufacturer:
            return
        values['origin'] = origin
        return super()._run_buy(
            product_id, product_qty, product_uom, location_id, name, origin, values)

    def _make_po_get_domain(self, values, partner):
        domain = super()._make_po_get_domain(values, partner)
        if values.get('origin'):
            domain += (
                ('origin', '=', values.get('origin')),
            )
        return domain
