# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Sale Order Planner",
    "summary": "Sale Order Planner",
    "version": "11.0.1.0.0",
    "category": "Sale",
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
        "base",
        "sale",
        "product_route_family",
        "integration_netsuite_fields",
        "product_product_customer"
    ],
    "data": [
        "data/product_product.xml",
        "wizards/wizard_import_planner.xml",
        "views/sale_order.xml",
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
