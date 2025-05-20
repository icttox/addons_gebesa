# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Account Invoice Prepayments",
    "summary": "Add new field that it indicates bills in advance",
    "version": "12.0.1.0.0",
    "category": "Account",
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
        "sale",
        "account_invoice_prepayment"
    ],
    "data": [
        "views/account_invoice_view.xml"
    ],
    "demo": [

    ],
    "qweb": [

    ]
}
