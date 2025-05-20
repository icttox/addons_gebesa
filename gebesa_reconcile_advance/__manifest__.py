# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Gebesa Reconcile Advance",
    "summary": "Advance for Customers and Suppliers",
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
        "account_analytic_everywhere"
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/menues_and_actions.xml",
        "views/gebesa_reconcile_advance_view.xml",
        "views/account_payment_view.xml",
        "views/res_partner_view.xml",
        "views/res_company.xml",
        "views/account_invoice.xml"
    ],
    "demo": [

    ],
    "qweb": [

    ]
}
