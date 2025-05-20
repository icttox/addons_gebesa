# -*- coding: utf-8 -*-
# © <2017> <Aldo Nerio>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api
# from odoo import tools
from odoo.tools.sql import drop_view_if_exists


class SaleOrderLineBackorder(models.Model):
    _name = 'sale.order.line.ba'
    _auto = False
    _description = 'descripcion pendiente'
    # _order = 'order'

    week = fields.Integer(string='Week Number')
    net_s = fields.Float(string='Vta Neta MXN')
    code = fields.Char(string='Code')
    order = fields.Char(string='Order')
    fecha_order = fields.Date(string='Date Order')

    @api.model_cr
    def init(self):
        cr = self._cr
        drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW sale_order_line_ba as
            (SELECT (l.id) as id, so.name as order, so.date_order as fecha_order,
             CASE WHEN rcr.rate_mex is NULL OR rcr.rate_mex = 0
             THEN (l.net_sale * 1)
             ELSE (l.net_sale * rcr.rate_mex) end as net_s,
             EXTRACT(week FROM CAST((so.date_order AT TIME ZONE 'UTC-6')AS DATE)) as week,
             CONCAT('[',pp.default_code,']',pp.name_template) as code
             FROM sale_order_line as l
                  join sale_order as so on (so.id = l.order_id)
                  join product_product as pp on (pp.id = l.product_id)
                  join product_pricelist as pl on (pl.id = so.pricelist_id)
                  join res_currency as rc on (rc.id = pl.currency_id)
                  left join res_currency_rate as rcr on (rcr.currency_id = rc.id and CAST(so.date_order AS DATE) = CAST(rcr.name as DATE) AND rcr.company_id = so.company_id)
             WHERE  so.state not in ('cancel','sent','draft') --EXTRACT(week FROM CAST(so.date_order AS DATE))
             AND l.closed != TRUE
            )""")
