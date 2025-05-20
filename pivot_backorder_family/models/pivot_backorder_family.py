# -*- coding: utf-8 -*-
# © <2017> <Aldo Nerio>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.tools.sql import drop_view_if_exists


class SaleOrderFamily(models.Model):
    _name = 'sale.order.family'
    _auto = False
    _description = 'descripcion pendiente'
    # _order = 'order'

    week = fields.Char(string='Numero Semana')
    amount = fields.Float(string='Imp X Sur')
    familia = fields.Char(string='Familia')
    family_id = fields.Many2one('product.family', string='Familia',)
    warehouse_id = fields.Many2one('stock.warehouse', string='Almacen',)
    product_id = fields.Many2one('product.product', string='Producto',)
    orden = fields.Char(string='Pedido De Venta')
    order_id = fields.Many2one('sale.order', string='Pedido De Venta',)
    date_order = fields.Datetime(string='Fecha Pedido')
    date_validator = fields.Datetime(string='Fecha Validacion')
    company_id = fields.Many2one('res.company', string='Company',)

    @api.model_cr
    def init(self):
        cr = self._cr
        drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW sale_order_family as
            (SELECT l.id,
             pf.name as familia,
             pf.id AS family_id,
             pf.warehouse_id,
             pp.id AS product_id,
             so.name as orden,
             so.id AS order_id,
             so.date_order as date_order,
             so.company_id AS company_id,
             so.date_validator AS date_validator,
             so.week_number as week,
             CASE WHEN rcr.rate_mex is null
                                   THEN (l.pending_qty * (l.net_sale / l.product_uom_qty)) * 1
                                   ELSE ((l.pending_qty * (l.net_sale / l.product_uom_qty)) * so.rate_mex) END as amount
             FROM sale_order_line as l
                  join sale_order as so on (so.id = l.order_id)
                  join product_product as pp on (pp.id = l.product_id)
                  join product_template as pt on (pt.id = pp.product_tmpl_id)
                  join product_family as pf on (pf.id = pt.family_id)
                  join product_pricelist as pl on (pl.id = so.pricelist_id)
                  join res_currency as rc on (rc.id = pl.currency_id)
                  left join res_currency_rate as rcr on (rcr.currency_id = rc.id and CAST(so.date_order AS DATE) = CAST(rcr.name as DATE) AND rcr.company_id = so.company_id)
             WHERE  so.geb_invoice_status in ('no_invoice','partial_invoice')
             and  so.state in ('done','sale') AND l.product_uom_qty != 0 AND l.closed IS NOT TRUE
             --GROUP BY so.id, pf.warehouse_id, pf.name
             ORDER BY so.name
            )""")
