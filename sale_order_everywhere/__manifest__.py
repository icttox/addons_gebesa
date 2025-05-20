# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Sale Order Everywhere",
    "summary": "Sale Order Everywhere",
    "version": "12.0.1.0.0",
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
        "stock",
        "mrp",
        "stock_picking_invoice",
        "sale_stock",
        "sales_order_dealer",
    ],
    "data": [
        "views/stock_move.xml",
        "views/mrp_production.xml",
        "views/stock_picking.xml",
        "data/ir_cron_data.xml"
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
