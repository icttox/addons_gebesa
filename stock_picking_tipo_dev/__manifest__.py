# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Return Type",
    "summary": "Return Type",
    "version": "12.0.1.0.0",
    "category": "Personalized",
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
        "base", "account", "stock"
    ],
    "data": [
        "views/account_invoice.xml",
        "views/stock_move.xml",
        "views/stock_picking.xml",
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
