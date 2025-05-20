# -*- coding: utf-8 -*-
# © <2017> <Aldo Nerio>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Pivot Backorder Family",
    "summary": "Pivot Backorder Family",
    "version": "12.0.1.0.0",
    "category": "Sales",
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
        "stock",
        "account",
        "product",
        "week_number_validate",
        "product_structure_gebesa",
        "order_line_cancel",
        "multicurrency_mexico",
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/pivot_backorder_family.xml",
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
