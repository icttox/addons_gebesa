# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Reports Wizard RM ORDER",
    "summary": "Reports Wizard RAW MATERIAL ORDER",
    "version": "11.0.1.0.0",
    "category": "Uncategorized",
    "website": "https://odoo-community.org/",
    "author": "Samuel Barron, Gebesa",
    "license": "AGPL-3",
    "application": False,
    "installable": False,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "base",
        "mrp",
        "sale",
        "gebesa_reports",
    ],
    "data": [
        "wizard/wizard_rw_order.xml"
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
