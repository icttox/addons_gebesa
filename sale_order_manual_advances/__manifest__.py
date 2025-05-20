# -*- coding: utf-8 -*-
# © <2017> <Armando Robledo>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Sales Orders Manual Advances",
    "summary": "Sales Orders Manual Advances",
    "version": "12.0.1.0.0",
    "category": "Sales",
    "website": "https://odoo-community.org/",
    "author": "Armando Robledo, Gebesa",
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
        "account_invoice_prepayment",
        "sales_order_dealer"
    ],
    "data": [
        "views/sale_order_manual_advances_view.xml",
        "security/ir.model.access.csv",
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
