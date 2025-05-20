# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Account Invoice Replace",
    "summary": "Account Invoice Replace",
    "version": "12.0.1.0.0",
    "category": "Uncategorized",
    "website": "https://odoo-community.org/",
    "author": "Esther Cisneros, Gebesa",
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
        "views/account_invoice_replace.xml",
        "data/ir_cron_data.xml",
        "data/send_account_invoice_cancel_tgalbo.xml",

    ],
    "demo": [

    ],
    "qweb": [

    ]
}
