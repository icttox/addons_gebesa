# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Account Move Utilities",
    "summary": "Add new methods for class account_move",
    "version": "12.0.1.0.0",
    "category": "Account",
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
        "gebesa_reports",
    ],
    "data": [
        "data/action_server.xml",
        "views/account_account_view.xml",

    ],
    "demo": [

    ],
    "qweb": [

    ]
}
