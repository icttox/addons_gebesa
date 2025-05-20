# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Product Variant Default Code",
    "summary": "Product Variant Default Code",
    "version": "12.0.1.0.0",
    "category": "MPR",
    "website": "https://odoo-community.org/",
    "author": "Deysy Mascorro, Gebesa",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "product",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/product_view.xml",
        "views/product_attribute_value_view.xml",
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
