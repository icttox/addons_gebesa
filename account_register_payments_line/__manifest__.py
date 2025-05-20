# -*- coding: utf-8 -*-
# © <2016> <Cesar Barron Bautista>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Partial payments to multiple invoices",
    "summary": "This module lets you pay partials invoices",
    "version": "12.0.1.0.0",
    "category": "Uncategorized",
    "website": "www.gebesa.com/",
    "author": "Cesar Barron, Gebesa",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "base", "account",
        "account_analytic_everywhere",
        "gebesa_reconcile_advance",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "views/account_payment.xml",
        "views/account_payment_register_line_view.xml",
    ],
    "demo": [
        # "demo/res_partner_demo.xml",
    ],
    "qweb": [
        # "static/src/xml/module_name.xml",
    ]
}
