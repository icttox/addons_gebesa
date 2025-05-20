# -*- coding: utf-8 -*-
# © 2018 Aldo Nerio
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Account Invoice Dealer",
    "summary": "Account Invoice Dealer",
    "version": "12.0.1.0.0",
    "category": "Accounting",
    "website": "https://odoo-community.org/",
    "author": "Aldo Nerio, Gebesa",
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
        "sales_order_dealer",
        "invoice_refund_validate",
    ],
    "data": [
        "views/account_invoice.xml",
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
