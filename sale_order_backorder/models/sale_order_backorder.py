# -*- coding: utf-8 -*-
# © <2017> <Aldo Nerio>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api
# from odoo import tools
from odoo.tools.sql import drop_view_if_exists


class SaleOrderBackorder(models.Model):
    _name = 'sale.order.backorder'
    _auto = False
    _description = 'descripcion pendiente'
    # _order = 'order'

    datee = fields.Datetime(string='Date Order')
    warehouse_id = fields.Many2one(
        'stock.warehouse',
        string='Almacen',
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
    )
    # ware = fields.Char(string=_('Warehouse'))
    # product_code = fields.Char(string=_('Product Code'))
    # product_name = fields.Char(string=_('Product'))
    product_id = fields.Many2one(
        'product.product',
        string='Producto',
    )
    # family = fields.Char(string=_('Family'))
    family_id = fields.Many2one(
        'product.family',
        string='Familia',
    )
    # order = fields.Char(string=_('Sale Order'))
    order_id = fields.Many2one(
        'sale.order',
        string='Pedido',
    )
    # partner = fields.Char(string=_('Partner'))
    partner_id = fields.Many2one(
        'res.partner',
        string='Cliente',
    )
    reception = fields.Char(string='Reception')
    subtotalpesos = fields.Float(string='Sub Total')
    fletepesos = fields.Float(string='Freight')
    importepesos = fields.Float(string='Import')
    netpesos = fields.Float(string='Net Sale')
    surtirpesos = fields.Float(string='Surtir')
    pricetotal = fields.Float(string='Total Price')
    week = fields.Integer(string='Week Number')
    margen = fields.Float(string='Margen de Contribucion')
    costo_surtir = fields.Float(string='Costo X Surtir')
    moneda = fields.Char(string='Dinero Corriente')
    segment_status = fields.Char(string='Estatus Segmento')
    shipment_status = fields.Char(string='Estatus Embarque')
    date_reception = fields.Date(string='Fecha Recepcion O.C.')
    cantidad_surtir = fields.Char(
        string='Cantidad  X Surtir',
    )

    # def _select(self):
    #    select_str = """
    #         SELECT so.name as order_id
    #    """
    #    return select_str

    def _from(self):
        from_str = """ sale_order_line l
                      left join sale_order so on (l.order_id=so.id)
                      """
        return from_str

    def _group_by(self):
        group_by_str = """
            GROUP BY l.id, so.id, pf.name, pp.default_code
        """
        return group_by_str

    @api.model_cr
    def init(self):
        cr = self._cr
        drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW sale_order_backorder as
            (select min(l.id) as id, so.date_order as datee,
                 so.company_id AS company_id,
                 so.id as order_id, EXTRACT(week FROM CAST(so.date_order AS DATE)) as week,
                 pf.id as family_id, max(sw.id) as warehouse_id,
                 pp.id as product_id,
                 max(rp.id) as partner_id, rc.name as moneda,
                 CASE WHEN so.segment_status = 'no_segment' THEN 'No Segmentado'
                      WHEN so.segment_status = 'partial_segment' THEN 'Parcialmente Segmentado'
                      WHEN so.segment_status = 'total_segment' THEN 'Totalmente Segmentado' END as segment_status,
                 CASE WHEN so.shiptment_status = 'no_shipment' THEN 'No Embarcado'
                      WHEN so.shiptment_status = 'partial_shipment' THEN 'Parcialmente Embarcado'
                      WHEN so.shiptment_status = 'total_shipment' THEN 'Totalmente Embarcado' END as shipment_status,
                 so.date_reception as date_reception,
                 SUM(l.pending_qty) as cantidad_surtir,
                 SUM(CASE WHEN rcr.rate_mex is null
                      THEN l.price_subtotal * 1
                      ELSE rcr.rate_mex * l.price_subtotal END) as subtotalpesos,
                 SUM(CASE WHEN rcr.rate_mex is null
                      THEN l.freight_amount * 1
                      ELSE rcr.rate_mex * l.freight_amount END) as fletepesos,
                 SUM(CASE WHEN rcr.rate_mex is null
                      THEN l.installation_amount * 1
                      ELSE rcr.rate_mex * l.installation_amount END) as importepesos,
                 SUM(CASE WHEN rcr.rate_mex is null
                      THEN l.net_sale * 1
                      ELSE rcr.rate_mex * l.net_sale END) as netpesos,
                 SUM(CASE WHEN rcr.rate_mex is null
                      THEN (l.pending_qty * (l.net_sale / l.product_uom_qty)) * 1
                      ELSE ((l.pending_qty * (l.net_sale / l.product_uom_qty)) * rcr.rate_mex) END) as surtirpesos,
                 SUM(CASE WHEN rcr.rate_mex is null
                      THEN l.price_unit * 1
                      ELSE rcr.rate_mex * l.price_unit END) as pricetotal,
                 (1-(SUM(l.standard_cost)/SUM(COALESCE(rcr.rate_mex,1)*l.net_sale))) as margen,
                 SUM(l.pending_qty * (l.standard_cost / l.product_uom_qty)) as costo_surtir
             FROM sale_order_line as l
                  join sale_order as so on (so.id = l.order_id)
                  join product_product as pp on (pp.id = l.product_id)
                  join product_template as pt on (pt.id = pp.product_tmpl_id)
                  join product_family as pf on (pf.id = pt.family_id)
                  join stock_warehouse as sw on (sw.id = so.warehouse_id)
                  join res_partner as rp on (rp.id = so.partner_id)
                  join product_pricelist as pl on (pl.id = so.pricelist_id)
                  join res_currency as rc on (rc.id = pl.currency_id)
                  left join res_currency_rate as rcr on (rcr.currency_id = rc.id and CAST(so.date_order AS DATE) = CAST(rcr.name as DATE) AND rcr.company_id = so.company_id)
             WHERE so.geb_invoice_status in ('no_invoice','partial_invoice') and  so.state in ('done','sale') and l.product_uom_qty > 0.00 AND l.closed IS NOT TRUE
             GROUP BY pf.id, so.id, pp.id, rc.name
             ORDER BY so.name
            )""")
