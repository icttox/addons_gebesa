# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Product Level Price",
    "summary": "Module for Product Price Level",
    "version": "12.0.1.0.0",
    "category": "product",
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
        "product_product_mu",
    ],
    "data": [
        "security/product_level_price_security.xml",
        "security/ir.model.access.csv",
        "views/product_level_price.xml",

    ],
    "demo": [
    ],
    "qweb": [
    ]
}
