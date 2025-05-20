# -*- coding: utf-8 -*-
# © 2017 Aldo Nerio
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Website Price Require Login",
    "summary": "Website Price Require Login",
    "version": "12.0.1.0.0",
    "category": "E-Commerce",
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
        "website_sale",
    ],
    "data": [
        "views/website_price_require_login.xml",
    ],
    "demo": [

    ],
    "qweb": [

    ]
}
