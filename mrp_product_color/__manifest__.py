# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "MRP product color",
    "summary": "MRP product color",
    "version": "12.0.1.0.0",
    "category": "Product",
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
        "base", "product", "stock"
    ],
    "data": [
        "views/mrp_product_color.xml",
        "security/ir.model.access.csv",
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
