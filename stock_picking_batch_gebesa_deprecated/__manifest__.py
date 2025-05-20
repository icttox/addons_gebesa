# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock batch picking personalized",
    "summary": "Stock batch picking",
    "version": "11.0.1.0.0",
    "category": "inventory",
    "website": "https://odoo-community.org/",
    "author": "Samuel Barron, Gebesa",
    "license": "AGPL-3",
    "application": False,
    "installable": False,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "base",
        "stock",
        "stock_batch_picking"
    ],
    "data": [
        "views/stock_batch_picking.xml",
        "report/report_picking_batch.xml",
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
