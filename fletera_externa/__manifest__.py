# -*- coding: utf-8 -*-
# © 2017 Aldo Nerio
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Fletera Externa",
    "summary": "Fletera Externa",
    "version": "12.0.1.0.0",
    "category": "Shipment",
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
        "mrp_shipment",
        "paperwork_usa",
    ],
    "data": [
        "views/mrp_shipment.xml",
        "reports/fletera_externa.xml",
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
