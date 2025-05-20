# Copyright 2021, Cesar Barron
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def get_backorder_data(self, params=None, sorting=None):
        '''
            Get the backorder data for customer portal
        '''
        query = """
        SELECT
            so.id AS so_id,
            so.week_number,
            so.name,
            so.date_order,
            rp.name AS partner,
            so.client_order_ref,
            CONCAT(rcsc.name, ', ', rcs.name) AS destination,
            ms.folio AS shipped_folio,
            (ms.departure_date + interval '1' day) AS shipment_departure_date,
            sol.id AS sol_id,
            pp.default_code,
            COALESCE(ir.value, pp.individual_name, ir2.value, pp.name_template, 'Sin definir') AS product_es,
            sol.pending_qty,
            ms.reference AS msl_reference
        FROM sale_order AS so
        LEFT JOIN res_partner AS rp ON so.partner_id = rp.id
        LEFT JOIN res_partner AS rp_ship ON so.partner_shipping_id = rp_ship.id
        LEFT JOIN res_country_state_city AS rcsc ON rp_ship.city_id = rcsc.id
        LEFT JOIN res_country_state AS rcs ON rp_ship.state_id = rcs.id
        LEFT JOIN account_analytic_account AS aaa ON so.analytic_account_id = aaa.id
        LEFT JOIN sale_order_line AS sol ON so.id = sol.order_id
        LEFT JOIN product_product AS pp ON sol.product_id = pp.id
        LEFT JOIN product_template AS pt ON pp.product_tmpl_id = pt.id
        LEFT JOIN ir_translation AS ir ON ir.res_id = pp.id
            AND ir.lang = 'es_MX' AND ir.name = 'product.product,individual_name'
        LEFT JOIN ir_translation AS ir2 ON pt.id = ir2.res_id
            AND ir2.lang = 'es_MX' AND ir2.name = 'product.template,name'
        LEFT JOIN (
            SELECT
                msl.order_line_id,
                ms.reference,
                ms.folio,
                ms.departure_date
            FROM (
                SELECT
                    msl.order_line_id,
                    MAX(ms.id) AS shipment_id
                FROM mrp_shipment_line AS msl
                LEFT JOIN mrp_shipment AS ms ON msl.shipment_id = ms.id
                GROUP BY msl.order_line_id) AS msl
            LEFT JOIN mrp_shipment AS ms ON msl.shipment_id = ms.id) AS ms ON sol.id = ms.order_line_id
        WHERE so.geb_invoice_status IN ('no_invoice','partial_invoice')
            AND so.geb_invoice_status IS NOT NULL
            AND so.state IN ('done', 'sale')
            AND so.company_id = %s
            AND sol.product_uom_qty != 0
            AND sol.pending_qty > 0.0000
            AND sol.closed IS NOT TRUE
            AND so.partner_id = %s
        ORDER BY
        """ + sorting
        self.env.cr.execute(query, tuple(params))
        return self.env.cr.dictfetchall()
