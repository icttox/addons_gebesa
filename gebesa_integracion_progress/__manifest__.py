# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Gebesa integracion Progress",
    "summary": "Gebesa integracion Progress",
    "version": "12.0.1.0.0",
    "category": "personalized",
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
        "base", "account", "stock",
        "integration_progress_fields",
        "stock_picking_type",
        "account_invoice_stock_picking_id",
        "mrp_shipment",
    ],
    "data": [
        # "views/stock_picking.xml"
        "views/account_invoice.xml"
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
