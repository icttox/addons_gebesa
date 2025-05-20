# -*- coding: utf-8 -*-
# © 2018 Aldo Nerio
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Configuración Cierre Anual",
    "summary": "Configuración Cierre Anual",
    "version": "12.0.1.0.0",
    "category": "MPR",
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
        "account",
        "mail",
        "message_post_model",
        "account_account_parent",
        "sale_order_gebesa",
        # "packing_gebesa",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "views/account_year_closing.xml",
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
