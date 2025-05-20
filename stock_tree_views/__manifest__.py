# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock Tree Views",
    "summary": "Add fields in tree views for Sales and Purchases.",
    "version": "12.0.1.0.0",
    "category": "Stock",
    "website": "https://odoo-community.org/",
    "author": "Deysy Mascorro, Gebesa",
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
        "sale",
        "purchase",
        "purchase_stock",
    ],
    "data": [
        "views/sale_quotation_view.xml",
        "views/sale_order_view.xml",
        "views/purchase_order_view.xml",
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
