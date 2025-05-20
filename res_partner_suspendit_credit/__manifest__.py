# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Partner Suspendit Credit",
    "summary": "Add a field indicating if they have suspended credit.",
    "version": "12.0.1.0.0",
    "category": "Account",
    "website": "https://odoo-community.org/",
    "author": "Deysy Mascorro>, Gebesa",
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
    ],
    "data": [
        "views/res_partner_view.xml",

    ],
    "demo": [
    ],
    "qweb": [
    ]
}
