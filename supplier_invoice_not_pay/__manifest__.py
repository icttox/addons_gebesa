# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Not Pay Supplier Invoice",
    "summary": "If the field is Not Paid, the invoice can not be paid.",
    "version": "12.0.1.0.0",
    "category": "Generic Modules",
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
        "account_invoice_sale_data",
        "account_payment_auth",
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/account_invoice_view.xml",
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
