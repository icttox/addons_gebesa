# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Shipment",
    "summary": "MRP Shipment",
    "version": "12.0.1.0.0",
    "category": "MRP",
    "website": "https://odoo-community.org/",
    "author": "Samuel Barron, Gebesa",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "base", "mrp", "sale",
        "stock_warehouse_analytic_id",
        "mrp_segment",
    ],
    "data": [
        "security/shipment_security.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence.xml",
        "data/ir_cron_data.xml",
        "views/mrp_shipment.xml",
        "views/sale_order.xml",
        "report/mrp_shipment.xml",
        "report/mrp_shipment_barcode.xml",
        "wizards/mrp_shipment_sale_order.xml",
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
