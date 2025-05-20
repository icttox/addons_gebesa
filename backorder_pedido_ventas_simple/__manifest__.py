# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "barckorder pedido de ventas simples",
    "summary": "Reporte de Ventas por pedido Simple",
    "version": "12.0.1.0.0",
    "category": "Sales",
    "website": "https://odoo-community.org/",
    "author": "Jesus Alcala, Gebesa",
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
        "sale_order_gebesa",
        "mrp_gebesa",
        "mrp_segment",
        "mrp_shipment",
        "week_number_validate",
    ],
    "data": [
        "views/sale_order.xml",
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
