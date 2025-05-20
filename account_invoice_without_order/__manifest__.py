# -*- coding: utf-8 -*-
# © 2018 Samuel Barron
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Account Invoice without order",
    "summary": "Add privileges to create invoices without order",
    "version": "12.0.1.0.0",
    "category": "Accounting",
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
        "account",
    ],
    "data": [
        'security/account_invoice_security.xml',
        'views/account_invoice.xml',
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
