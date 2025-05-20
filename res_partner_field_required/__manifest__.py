# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Field Required in Partners",
    "summary": "Customers and Suppliers Field Required",
    "version": "12.0.1.0.0",
    "category": "",
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
        "base",
        "account",
        "base_vat",
    ],
    "data": [
        "views/base_partner_view.xml",
        "security/security.xml",
    ],
    "demo": [

    ],
    "qweb": [

    ]
}
