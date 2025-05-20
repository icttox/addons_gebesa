# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Shipment Freight Cost",
    "summary": "Shipment Freight Cost",
    "version": "12.0.1.0.0",
    "category": "Generic Modules",
    "website": "https://odoo-community.org/",
    "author": "Leslie Marquez, Gebesa",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "base",
        "account",
        "sale",
        "mrp",
        "mrp_shipment",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/account_invoice_view.xml",
        "views/inv_rel_shipment_view.xml",
        "views/inv_rel_so_view.xml",
        "views/mrp_shipment_view.xml",
        "views/mrp_shipment_line_view.xml",
        "views/sale_order_view.xml",
    ],
    "demo": [

    ],
    # "post_init_hook": "post_init_hook",
    "qweb": [

    ]
}
