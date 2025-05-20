# -*- coding: utf-8 -*-
# Copyright 2024, Marco Esquivel
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    "name": "Gebesa hubspot in odoo email",
    "summary": "Create A Sales Budget When Changing The Stage Of Business In Hubspot",
    "version": "12.0.1.0.0",
    "category": "Personalized",
    "website": "https://odoo-community.org/",
    "author": "Marco Esquivel, Gebesa",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "base", "sale",
    ],
    "data": [
        "views/res_partner_view.xml",
        "views/sale_order_view.xml",
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
