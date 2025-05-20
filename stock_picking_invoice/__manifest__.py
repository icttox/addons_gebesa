# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock - Invoice",
    "summary": "Stock - Invoice",
    "version": "12.0.1.0.0",
    "category": "Uncategorized",
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
        "base", "stock", "sale",
        "purchase",
        "cfdi32", "sales_channel",
        "account_analytic_everywhere"
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizards/stock_invoice.xml",
        "wizards/stock_return_picking.xml",
        "views/stock_picking.xml",
        "views/stock_move.xml",
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
