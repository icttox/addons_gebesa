# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Product Attribute Line Gebesa",
    "summary": "Product Attribute Line Gebesa",
    "version": "12.0.1.0.0",
    "category": "Uncategorized",
    "website": "https://odoo-community.org/",
    "author": "Aldo Nerio, Gebesa",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "base",
        "account",
        "stock",
        "product",
        "sale",
        "integration_progress_fields",
        "sale_order_gebesa",
        "integration_netsuite_fields",
        "integration_cost_gebesa",
        "account_invoice_sale_data"
    ],
    "data": [
        "views/product_template.xml",
    ],
    "demo": [

    ],
    "qweb": [

    ]
}
