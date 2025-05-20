# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Pivot Week For Order",
    "summary": "Pivot Week For Order",
    "version": "12.0.1.0.0",
    "category": "Uncategorized",
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
        "mrp",
        "week_number_validate",
        "backorder_pedido_ventas_simple",
        "sale_order_gebesa",
        "order_line_cancel",
        "product_structure_gebesa",
    ],
    "data": [
        "views/pivot_week_order.xml",
        "views/pivot_week_total.xml",
    ],
    "demo": [

    ],
    "qweb": [

    ]
}
