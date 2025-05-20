# -*- coding: utf-8 -*-
# © <2017> <Aldo Nerio>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api
# from odoo import tools
from odoo.tools.sql import drop_view_if_exists


class SaleOrderLineBackorder(models.Model):
    _name = 'sale.order.line.quantity'
    _auto = False
    _description = 'descripcion pendiente'
    # _order = 'order'

    week = fields.Integer(string='Week Number')
    quantity = fields.Float(string='Quantity')
    code = fields.Char(string='Code')
    order = fields.Char(string='Order')
    fecha_order = fields.Date(string='Date Order')

    @api.model_cr
    def init(self):
        cr = self._cr
        drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW sale_order_line_quantity as
            (SELECT (l.id) as id, so.name as order, so.date_order as fecha_order,
             product_uom_qty as quantity,
             EXTRACT(week FROM CAST((so.date_order AT TIME ZONE 'UTC-6')AS DATE)) as week,
             --EXTRACT(week FROM CAST(so.date_order AS DATE)) as week,
             --CONCAT('W',EXTRACT(week FROM CAST(so.date_order AS DATE)),' ',EXTRACT(year FROM CAST(so.date_order AS DATE)) )as week,
             CONCAT('[',pp.default_code,']',pp.name_template) as code
             FROM sale_order_line as l
                  join sale_order as so on (so.id = l.order_id)
                  join product_product as pp on (pp.id = l.product_id)
             WHERE  so.state not in ('cancel','sent','draft') --EXTRACT(week FROM CAST(so.date_order AS DATE))
             ORDER BY EXTRACT(week FROM CAST(so.date_order AS DATE))
            )""")
