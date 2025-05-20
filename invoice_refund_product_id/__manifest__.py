# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Invoice refund product",
    "summary": "Invoice refund product",
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
        "base", "account",
        "account_analytic_everywhere"
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/account_invoice_refund.xml",
        "views/account_tax.xml"
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
