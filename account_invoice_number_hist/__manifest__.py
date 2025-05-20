# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Invoice number hist",
    "summary": "Invoice number hist",
    "version": "12.0.1.0.0",
    "category": "accounting",
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
        "base", "account", "cfdi32", "account_voucher",
        "transactions_not_entry_line",
        'l10n_mx_edi'
    ],
    "data": [
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
