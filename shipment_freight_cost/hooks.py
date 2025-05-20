# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    _logger.info('UPDATE total_mxn FROM mrp_shipment_line')
    cr.execute(
        """
            UPDATE mrp_shipment_line as msl
                SET total_mxn = (
                    ((sol.price_total / sol.product_uom_qty)
                     * msl.quantity_shipped) / COALESCE(rcr.rate,1.00))
            FROM sale_order_line as sol
            LEFT JOIN sale_order AS so ON sol.order_id = so.id
            LEFT JOIN product_pricelist AS pp ON so.pricelist_id = pp.id
            LEFT JOIN res_company AS rcp ON so.company_id = rcp.id
            LEFT JOIN res_currency AS rc ON pp.currency_id = rc.id
            LEFT JOIN res_currency_rate as rcr on
                CAST(so.date_validator as DATE) = CAST(rcr.name as DATE)
                and rcr.currency_id = rc.id
                and rcr.company_id = so.company_id
            WHERE msl.order_line_id = sol.id
        """)
    _logger.info('UPDATE amount_total_mxn FROM mrp_shipment')
    cr.execute(
        """
            UPDATE mrp_shipment as ms
                SET amount_total_mxn = (
                    SELECT SUM(msl.total_mxn)
                    FROM mrp_shipment_line msl
                    WHERE msl.shipment_id = ms.id)
        """)
    _logger.info('UPDATE total_gasto_flete_mxn FROM mrp_shipment')
    cr.execute(
        """
        UPDATE mrp_shipment AS ms
        SET total_gasto_flete_mxn = t.total
        FROM (
                SELECT
                    SUM(ai.amount_total/ai.rate) as total,
                    irs.shipment_id as ship
                FROM inv_rel_shipment as irs
                LEFT JOIN account_invoice AS ai ON irs.invoice_id = ai.id
                GROUP BY irs.shipment_id
        ) as t
        where t.ship = ms.id
        """)
    _logger.info('UPDATE gasto_pro_flete_mxn FROM mrp_shipment_line')
    cr.execute(
        """
        UPDATE mrp_shipment_line as msl
        SET gasto_pro_flete_mxn = ((msl.total_mxn / ms.amount_total_mxn) * ms.total_gasto_flete_mxn)
        FROM mrp_shipment as ms
        WHERE msl.shipment_id = ms.id
            and msl.total_mxn > 0
            and ms.amount_total_mxn > 0
        """)
    _logger.info('UPDATE total_sale FROM account_invoice')
    cr.execute(
        """
        UPDATE account_invoice AS ai
        SET total_sale = t.total
        FROM (
            select
            irs.invoice_id as inv,
            SUM(so.amount_total) as total
            FROM inv_rel_so as irs
        LEFT JOIN sale_order AS so ON irs.order_id = so.id
        GROUP BY irs.invoice_id
        ) as t
        where t.inv = ai.id
        """)
