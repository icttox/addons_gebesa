# -*- coding: utf-8 -*-
# © <2016> <César Barrón>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock Picking Review Buttom",
    "summary": "Stock Picking Review Buttom",
    "version": "12.0.1.0.0",
    "category": "MRP",
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
        "stock",
        "stock_picking_tipo_dev",
    ],
    "data": [
        "views/stock.xml",
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
