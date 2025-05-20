# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Account Journal - Field Active",
    "summary": "Add field active in account_journal",
    "version": "11.0.1.0.0",
    "category": "",
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
    ],
    "data": [
        "security/security.xml",
        "views/account_journal_view.xml",
    ],
    "demo": [

    ],
    "qweb": [

    ]
}
