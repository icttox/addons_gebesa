# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Website sale attribute image",
    "summary": "Website sale attribute image",
    "version": "12.0.1.0.0",
    "category": "Website",
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
        "base",
        "website_sale",
        "product_attribute_value_gebesa",
    ],
    "data": [
        "views/templates.xml"
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
