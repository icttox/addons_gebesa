# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock picking account location",
    "summary": "Stock picking account location",
    "version": "12.0.1.0.0",
    "category": "Account",
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
        "stock",
        "stock_account",
        "stock_location_account_account",
        "stock_picking_move_id",
        "stock_picking_type",
        # "system_administrator",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/stock_picking.xml",
        "views/stock_move.xml",
        "views/product_product_views.xml",
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
