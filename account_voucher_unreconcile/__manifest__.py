# -*- coding: utf-8 -*-
# © 2020 Cesar Barron
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Account Voucher Unreconcile",
    "summary": "Add a button to the voucher's payments for unreconcile",
    "version": "12.0.1.0.0",
    "category": "Accounting",
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
        "account",
        "account_voucher",
        # "system_administrator",
        "account_voucher_payment",
    ],
    "data": [
        "wizards/account_voucher_unreconcile_view.xml",
        "views/account_voucher_views.xml",
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
