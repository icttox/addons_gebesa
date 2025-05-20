# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Modify Delivery Address in Sales Order",
    "summary": "Modify Delivery Address in Sales Order",
    "version": "12.0.1.0.0",
    "category": "Generic Modules",
    "website": "https://odoo-community.org/",
    "author": "Deysy Mascorro, Gebesa",
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
        "mrp_shipment"
    ],
    "data": [
        "security/security.xml",
        "views/sale_order_view.xml",
    ],
    "demo": [

    ],
    "qweb": [

    ]
}
