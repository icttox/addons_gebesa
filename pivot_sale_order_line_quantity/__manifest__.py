# -*- coding: utf-8 -*-
# © <2017> <Aldo Nerio>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Pivot Sale Order Line Quantity",
    "summary": "Pivot Sale Order Line Quantity",
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
        "product",
        "stock",
        "mrp",
        "backorder_pedido_ventas_simple"
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/pivot_sale_order_line_quantity.xml",
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
