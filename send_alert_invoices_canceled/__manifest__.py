# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Send Invoice Canceled",
    "summary": "Send alert of canceled invoices on the first day of each month.",
    "version": "12.0.1.0.0",
    "category": "accounting",
    "website": "https://odoo-community.org/",
    "author": "Leslie Marquez, Gebesa",
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
        'data/ir_cron.xml'
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
