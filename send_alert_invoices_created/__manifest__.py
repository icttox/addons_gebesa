# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Send Invoice Created",
    "summary": "Send alert of invoices created the previous day",
    "version": "12.0.1.0.0",
    "category": "accounting",
    "website": "https://odoo-community.org/",
    "author": "Samuel Barron, Leslie Marquez, Gebesa",
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
        "res_company_manufacturer",
    ],
    "data": [
        'data/ir_cron.xml'
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
