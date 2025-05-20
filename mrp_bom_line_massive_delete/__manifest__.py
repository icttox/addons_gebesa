# -*- coding: utf-8 -*-
# © 2017 Aldo Nerio
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "MRP Bom Line Massive Delete",
    "summary": "MRP Bom Line Massive Delete",
    "version": "12.0.1.0.0",
    "category": "MRP",
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
        "mrp",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizards/mrp_bom_line_massive_delete.xml",
    ],
    "demo": [

    ],
    "qweb": [

    ]
}
