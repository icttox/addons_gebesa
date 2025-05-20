# -*- coding: utf-8 -*-
# © 2019 Cesar Barron
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Product Supplier Info from CFDi",
    "summary": "Extracts the child's node Conceptos, to create supplier_info records",
    "version": "12.0.1.0.0",
    "category": "account",
    "website": "https://odoo-community.org/",
    "author": "Cesar Barron, Gebesa",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "base",
        "product",
        "account",
        # "system_administrator"
    ],
    "data": [
        "views/account_invoice_view.xml",
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
