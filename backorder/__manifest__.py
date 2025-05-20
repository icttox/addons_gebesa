# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Backorder",
    "summary": "Report Backorder",
    "version": "12.0.1.0.0",
    "category": "Report",
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
        "base", "sale",
        "sale_order_gebesa",
        "mrp_shipment",
        "mrp_gebesa",
        "sale_order_line_pending_qty",
        "mrp_segment",
    ],
    "data": [
        "views/sale_order.xml"
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
