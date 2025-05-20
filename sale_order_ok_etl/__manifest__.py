# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Sale Order Ok ETL",
    "summary": "Sale Order Ok ETL",
    "version": "12.0.1.0.0",
    "category": "Sale",
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
        "sale",
        "integration_netsuite_fields",
    ],
    "data": [
        "data/ir_cron_data.xml",
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
