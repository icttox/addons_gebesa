# -*- coding: utf-8 -*-
# © 2017 Aldo Nerio
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Invoice Refund Validate",
    "summary": "Invoice Refund Validate",
    "version": "12.0.1.0.0",
    "category": "Personalized",
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
        "invoice_refund_product_id",
        "account_invoice_refund_mode",
        "account",
        # "employee_warehouse",
        "cfdi32",
        "res_users_cancel_invoice",
        "flete_gebesa",
    ],
    "data": [
        "security/security.xml",
        "views/account_invoice.xml",
        "wizards/account_invoice_wizard.xml",
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
