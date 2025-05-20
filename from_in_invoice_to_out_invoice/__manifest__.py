# -*- coding: utf-8 -*-
# © 2022 Cesar Barron
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "In to Out Invoice",
    "summary": "Create a customer invoice from a vendor bill.",
    "version": "12.0.1.0.0",
    "category": "",
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
    ],
    "data": [
        "wizards/from_in_to_out_invoice_views.xml",
        "views/account_invoice_views.xml",
    ],
    "demo": [

    ],
    "qweb": [

    ]
}
