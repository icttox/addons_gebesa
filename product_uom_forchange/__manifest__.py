# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Product Uom Forchange",
    "summary": "Product Uom Forchange",
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
    ],
    "data": [
        "security/security.xml",
        "views/product_uom_forchange.xml",
        "wizard/product_uom_forchange.xml",
    ],
    "demo": [

    ],
    "qweb": [

    ]
}
