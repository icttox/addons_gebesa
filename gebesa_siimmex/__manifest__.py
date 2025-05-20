# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Gebesa SIIMMEX",
    "summary": "Gebesa SIIMMEX",
    "version": "12.0.1.0.0",
    "category": "",
    "website": "https://odoo-community.org/",
    "author": "Leslie Marquez, Gebesa",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "base", "account", "immex_gebesa"
    ],
    "data": [
        "views/product_product_view.xml",
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
