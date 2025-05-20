# -*- coding: utf-8 -*-
# © <2017> <Aldo Nerio>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Sales Orders Backorder",
    "summary": "Sales Orders Backorder",
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
        "product_structure_gebesa",
        "backorder_pedido_ventas_simple",
        "order_line_cancel",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "views/sale_order_backorder.xml",
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
