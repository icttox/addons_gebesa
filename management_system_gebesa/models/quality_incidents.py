# Copyright 2022, Marco Esquivel
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields


class QualityIncidents(models.Model):
    _name = 'quality.incidents'
    _rec_name = 'date_incident'
    _inherit = ['message.post.show.all']
    _description = 'descripcion pendiente'

    date_incident = fields.Date(
        string='Date incident',
        required=True,
    )

    date_invoice = fields.Date(
        string='Date invoice'
    )

    sale_order_id = fields.Many2one(
        'sale.order',
        string='Original order',
        required=True,
    )

    warehouse_id = fields.Many2one(
        'stock.warehouse',
        string='Warehouse',
        required=True,
    )

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.user.company_id,
    )

    product_id = fields.Many2one(
        'product.product',
        string='Name product',
        required=True,
    )

    amount = fields.Integer(
        string='Amount',
    )

    net_sale_dollars = fields.Float(
        string='Net sales dollars',
    )

    net_sale_mx = fields.Float(
        string='Net sale mx',
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
    #     default='product',
    #     required=True,
    # )

    replacement_id = fields.Many2one(
        'quality.alert.flaw',
        string='Reposicion',
        required=True
    )

    description = fields.Text(
        string='Description',
        required=True
    )

    contingent_ids = fields.One2many(
        'quality.contingent.incidents',
        'incidents_id',
        string='Actions contingent',
    )

    why = fields.Text(
        string='¿Why?',
    )

    why_1 = fields.Text(
        string='¿Why?',
    )

    why_2 = fields.Text(
        string='¿Why?',
    )

    why_3 = fields.Text(
        string='¿Why?',
    )

    why_4 = fields.Text(
        string='¿Why?',
    )

    cause = fields.Text(
        string='Cause',
    )

    corrective_ids = fields.One2many(
        'quality.corrective.incidents',
        'incidents_corrective_id',
        string='Actions corrective',
    )

    check = fields.Many2one(
        'hr.employee',
        string='Check',
    )

    date_close = fields.Date(
        string='Date close'
    )

    status = fields.Selection(
        [('open', 'Abierto'),
         ('process', 'Proceso'),
         ('closed', 'Cerrado')],
        string='Status',
        default='open',
    )

    revised_id = fields.Many2one(
        'hr.employee',
        string='Revised',
    )

    order_id = fields.Many2one(
        'sale.order',
        string='Current order',
        required=True,
    )
