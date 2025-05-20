# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Product Combination Exclude",
    "summary": "Allows the specification of incompatible product "
               "combinations when creating products",
    "version": "12.0.1.0.0",
    "category": "Product",
    "website": "https://odoo-community.org",
    "author": "Graeme Gellatly, Gebesa",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "product",
        "sale",
    ],
    "data": [
        'security/product_attribute_exclude.xml',
        'security/product_attribute_exclude_matrix.xml',
        'views/product_attribute_exclude_matrix.xml',
    ],
    "demo": [
        'demo/product_attribute_exclude_matrix.xml',
        'demo/create_variants.xml'
    ],
    "qweb": [
    ]
}
