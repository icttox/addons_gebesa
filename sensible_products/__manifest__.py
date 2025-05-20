# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Sensible Products",
    "summary": "Sensible Products",
    "version": "12.0.1.0.0",
    "category": "Product",
    "website": "https://odoo-community.org/",
    "author": "Jesus Alcalá, Gebesa",
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
        "stock"
    ],
    "data": [
        "views/sensible_products.xml",
        "security/security.xml",
        "security/ir.model.access.csv",

    ],
    "demo": [
    ],
    "qweb": [
    ]
}
