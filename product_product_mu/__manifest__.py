# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Product Product Mu",
    "summary": "Module product mu",
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
    ],
    "data": [
        "views/product_product_mu.xml",
        "security/product_product_mu_security.xml",
        "security/ir.model.access.csv"
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
