# -*- coding: utf-8 -*-
# © 2017 Aldo Nerio
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Pedidos Vinculados",
    "summary": "Pedidos Vinculados",
    "version": "12.0.1.0.0",
    "category": "Sale Order",
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
        "sale",
        "reconcile_advance_include_parent",
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/pedidos_vinculados.xml",
    ],
    "demo": [

    ],
    "qweb": [

    ]
}
