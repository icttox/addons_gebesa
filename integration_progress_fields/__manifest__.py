# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Integration Progress Fields",
    "summary": "Add new fields for integration with progress",
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
        "account",
        "stock",
        "product",
        "integration_cost_gebesa",
        "account_invoice_sale_data"
    ],
    "data": [
        "views/product_view.xml",
        "views/stock_picking_view.xml",
        "views/stock_move_view.xml",
        "views/res_partner.xml",
        "views/account_invoice_view.xml",
    ],
    "demo": [

    ],
    "qweb": [

    ]
}
