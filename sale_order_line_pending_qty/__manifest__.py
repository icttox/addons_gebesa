# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "sale order line pending qty",
    "summary": "Module summary",
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
        "base", "sale"
    ],
    "data": [
        "views/sale_order.xml"
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
