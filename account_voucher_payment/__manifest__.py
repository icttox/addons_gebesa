# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Account Voucher Payment",
    "summary": "Account Voucher Payment",
    "version": "12.0.1.0.0",
    "category": "Account",
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
        "base", "account_voucher",
        "account_register_payments_line"
    ],
    "data": [
        "security/account_voucher_payment_security.xml",
        "security/ir.model.access.csv",
        "wizards/account_voucher_payment.xml",
        "views/account_payment.xml",
        "views/account_voucher.xml",
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
