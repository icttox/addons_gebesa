# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Account Financial Report Mx",
    "summary": "Account Financial Report Mx",
    'version': '1.1',
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
        "mail",
        'message_post_model',
        'account_reports',
        'system_administrator'
    ],
    "data": [
        "views/account_account_edores_type.xml",
        "views/account_account.xml",
        "security/ir.model.access.csv"
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
