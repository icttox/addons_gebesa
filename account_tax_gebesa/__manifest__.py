# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Account tax gebesa",
    "summary": "Account tax gebesa",
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
        "base",
        "account",
        "account_diot",
        # "l10n_mx_tax_cash_basis",
    ],
    "data": [
        "views/account_move.xml"
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
