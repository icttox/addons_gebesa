# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Massive replacement",
    "summary": "MRP Bom Line Massive replacement",
    "version": "12.0.1.0.0",
    "category": "MRP",
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
        "product",
        "mrp",
    ],
    "data": [
        "wizards/mrp_bom_line_massive_replacement.xml",
    ],
    "demo": [],
    "qweb": []
}
