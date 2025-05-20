# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Bom Delete Massive Import",
    "summary": "Bom Delete Massive Import",
    "version": "12.0.1.0.0",
    "category": "Uncategorized",
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
        "product",
        "mrp",
    ],
    "data": [
        "security/bom_delete_massive_import_security.xml",
        "security/ir.model.access.csv",
        "views/bom_massive_import.xml",

    ],
    "demo": [

    ],
    "qweb": [

    ]
}
