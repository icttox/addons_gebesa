# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Factoring Gebesa",
    "summary": "Add a new module for Customers and Suppliers for factoring",
    "version": "11.0.1.0.0",
    "category": "Uncategorized",
    "website": "https://odoo-community.org/",
    "author": "Deysy Mascorro, Gebesa",
    "license": "AGPL-3",
    "application": False,
    "installable": False,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "base",
        "account",
        "account_register_payments_line",
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/factoring_customer_view.xml",
        "views/factoring_supplier_view.xml",
        "views/factoring_secuence.xml",
        "views/account_invoice_view.xml",
        "views/account_payment_register_line_view.xml",
    ],
    "demo": [

    ],
    "qweb": [

    ]
}
