# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Recalculate Quant",
    "summary": "recalculate",
    "version": "12.0.1.0.0",
    "category": "Stock",
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
        "stock",
    ],
    "data": [
        "data/ir_cron_data.xml"
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
