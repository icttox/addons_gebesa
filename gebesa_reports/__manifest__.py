# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Gebesa reports",
    "summary": "Gebesa reports",
    "version": "12.0.1.0.0",
    "category": "Personalizado",
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
        "base", "account", "board",
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/account_account.xml",
        "views/account_journal.xml",
        "views/gebesa_report.xml",
        "views/account_account_type.xml",
        "views/res_partner.xml",
        "views/res_lang_view.xml",
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
