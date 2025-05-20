# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Product Category Company",
    "summary": "Product Category Company",
    "version": "12.0.1.0.0",
    "category": "Generic Modules",
    "website": "https://odoo-community.org/",
    "author": "Daniel Gurrola, Gebesa",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "base",
        "stock",
        "product",
        "product_structure_gebesa",

    ],
    "data": [
        'security/ir.model.access.csv',
        'views/product_category_company_geb.xml',
        'views/product_template.xml',
        'security/mrp_security.xml',
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
