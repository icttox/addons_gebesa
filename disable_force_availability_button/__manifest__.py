# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Disable Force Availability Button",
    "summary": "Add privileges per group on the force-availability button.",
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
        "stock",
        "mrp",
        "sale_stock",
        "stock_picking_batch",
        # "system_administrator",
    ],
    "data": [
        "views/stock_picking_view.xml",
        "views/stock_move_line.xml",
        "views/product_product_view.xml",
        "views/stock_picking_batch.xml",
        "security/security.xml"
    ],
    "demo": [

    ],
    "qweb": [

    ]
}
