# -*- coding: utf-8 -*-
# © 2019 Cesar Barron
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Cypto Utils",
    "summary": "Crypto utils",
    "version": "12.0.1.0.0",
    "category": "account",
    "website": "https://odoo-community.org/",
    "author": "Cesar Barron, Gebesa",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "account",
        "cfdi32",
    ],
    "data": [
        "views/crypto_utils_views.xml",
        "security/ir.model.access.csv",
    ],
    "demo": [

    ],
    "qweb": [

    ]
}
