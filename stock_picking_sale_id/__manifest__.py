# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock Picking - Sale Order Reference",
    "summary": "Add a field in the picking referencing to its sale_order",
    "version": "12.0.1.0.0",
    "category": "Uncategorized",
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
        "stock",
        "sale",
        "sale_stock",

    ],
    "data": [
        "views/stock_picking_view.xml",
    ],
    "demo": [

    ],
    "qweb": [

    ]
}
