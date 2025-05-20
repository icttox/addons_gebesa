# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Product Route Family",
    "summary": "Product Route Family",
    "version": "12.0.1.0.0",
    "category": "Account",
    "website": "https://odoo-community.org/",
    "author": "Esther Cisneros, Gebesa",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "stock",
        'sale_stock',
        "product",
        "product_structure_gebesa",

    ],
    "data": [
        "views/stock_location_route.xml",
        "views/sale_order.xml",
        "views/available_sale.xml",
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
