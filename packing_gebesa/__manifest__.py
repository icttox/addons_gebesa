# -*- coding: utf-8 -*-
# © 2018 Aldo Nerio
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Packing Gebesa",
    "summary": "Packing Gebesa",
    "version": "12.0.1.0.0",
    "category": "MPR",
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
        "product",
        "mrp",
        "mrp_shipment",
    ],
    "data": [
        "security/packing_gebesa_security.xml",
        "security/ir.model.access.csv",
        "data/report_paperformat.xml",
        "views/product_packing_list.xml",
        "views/product_packing_list_line.xml",
        "views/logistic_unit_type.xml",
        "views/mrp_shipment.xml",
        "reports/packing.xml",
        "reports/mrp_shipment.xml"
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
