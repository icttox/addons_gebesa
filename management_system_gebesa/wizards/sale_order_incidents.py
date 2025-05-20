# Copyright 2022, Marco Esquivel
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api


class SaleOrderIncidents(models.TransientModel):
    _name = 'sale.order.incidents'
    _description = 'descripcion pendiente'

    date_incident = fields.Date(
        string='Date incident',
        required=True,
    )

    warehouse_id = fields.Many2one(
        'stock.warehouse',
        string='Warehouse',
        required=True,
    )

    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
    )

    amount = fields.Integer(
        string='Amount',
    )

    sale_order_id = fields.Many2one(
        'sale.order',
        string='Origin order',
        required=True,
    )

    departament_id = fields.Many2one(
        'hr.department',
        string='Department',
        required=True,
    )

    # replacement = fields.Selection(
    #     [('product', 'Product/parts incorrect'),
    #      ('hits', 'Hits'),
    #      ('default', 'Default MP'),
    #      ('design', 'Design incorrect'),
    #      ('error', 'Error production'),
    #      ('merchandise_not_arrive', 'Merchandise not arrive/parts'),
    #      ('fault_purchased_product', 'Fault in the purchased product/sale'),
    #      ('release', 'Release error'),
    #      ('incident_client', 'Incident for client'),
    #      ('welding', 'Welding'),
    #      ('painting', 'Painting'),
    #      ('finishes', 'Finishes'),
    #      ('dirty', 'Dirty'),
    #      ('armed', 'Armed'),
    #      ('supplied_by_service', 'Supplied by service'),
    #      ('production_quality_error', 'Production/Quality Error'),
    #      ('freight_loses_package', 'freight loses package'),
    #      ('buy_and_sell', 'Buy and sell'),
    #      ('wrong_measurements', 'wrong measurements'),
    #      ('lack_of_components', 'Lack of components'),
    #      ('shipments', 'Shipments'),
    #      ('products_not_quote', 'Productos no agregados a la cotización'),
    #      ('byrne_warranty', 'Garantía Byrne'),
    #      ('warranty', 'Garantia'), ],
    #     string='Replacement',
    #     required=True,
    # )

    replacement_id = fields.Many2one(
        'quality.alert.flaw',
        string='Reposicion',
        required=True
    )

    description = fields.Text(
        string='Description',
        required=True,
    )

    order_id = fields.Many2one(
        'sale.order',
        string='Current order',
        required=True,
    )

    product_uom_qty = fields.Float(
        string='Cantidad total',
    )

    net_sale = fields.Float(
        string='Venta neta',
    )

    net_sale_mx = fields.Float(
        string='Venta neta (Pesos)',
        compute='_compute_total',
        default=0.00
    )

    @api.depends('product_uom_qty', 'net_sale', 'amount')
    def _compute_total(self):
        for cal in self:
            cal.net_sale_mx = 0
            # cal.net_sale_mx = (cal.net_sale / cal.product_uom_qty) * cal.amount
            cal.net_sale_mx = round((cal.net_sale * cal.sale_order_id.rate_mex), 4)

    @api.multi
    def send_incidence(self):
        incident = self.env['quality.incidents']
        incident.create({
            'date_incident': self.date_incident,
            'warehouse_id': self.warehouse_id.id,
            'departament_id': self.departament_id.id,
            'sale_order_id': self.sale_order_id.id,
            'product_id': self.product_id.id,
            'amount': self.amount,
            'replacement_id': self.replacement_id.id,
            'description': self.description,
            'order_id': self.order_id.id,
            'net_sale_mx': self.net_sale_mx,
        })
