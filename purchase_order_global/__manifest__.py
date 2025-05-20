# -*- coding: utf-8 -*-
# © 2018 Aldo Nerio
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Purchase Order Global",
    "summary": "Purchase Order Global",
    "version": "12.0.1.0.0",
    "category": "Purchase",
    "website": "https://odoo-community.org/",
    "author": "Aldo Nerio, Gebesa",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "base",
        "web",
        "purchase",
    ],
    "data": [
        "report/purchase_order.xml",
    ],
    "demo": [

    ],
    "qweb": [

    ]
}
