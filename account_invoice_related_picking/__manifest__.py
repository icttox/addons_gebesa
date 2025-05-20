# -*- coding: utf-8 -*-
# © 2018 Aldo Nerio
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Account Invoice related",
    "summary": "Account Invoice related",
    "version": "12.0.1.0.0",
    "category": "Accounting",
    "website": "https://odoo-community.org/",
    "author": "Daniel Gurrola, Gebesa",
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
    ],
    "data": [
        "views/account_invoice.xml",
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
