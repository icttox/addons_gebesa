# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Sale Order Line Update qty",
    "summary": "Sale Order Line Update delivered qty and invoice qty",
    "version": "12.0.1.0.0",
    "category": "Sale",
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
        "sale",
        "sale_order_line_pending_qty",
    ],
    "data": [
        "wizards/sale_order_line_update_qty.xml",
        "security/security.xml",
        "views/sale_order.xml",
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
