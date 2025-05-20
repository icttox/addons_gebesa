# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Invoice Petition Control",
    "summary": "Invoice Petition Control",
    "version": "12.0.1.0.0",
    "category": "Generic Modules",
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
        "foreign_commerce_complement",
    ],
    "data": [
        "views/account_invoice.xml",
        "data/ir_cron_data.xml",
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
