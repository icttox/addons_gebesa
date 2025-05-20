# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Sale channel",
    "summary": "Sales channel for invoices",
    "version": "12.0.1.0.0",
    "category": "accounting",
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
        "base", "account",
        "sale",
    ],
    "data": [
        "views/account_invoice.xml",
        "views/sales_channel.xml",
        "views/res_partner.xml",
        "views/sale_order_view.xml",
        "security/security.xml",
        "security/ir.model.access.csv",
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
