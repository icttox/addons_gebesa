# -*- coding: utf-8 -*-
# © 2017 Aldo Nerio
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock Picking Validate",
    "summary": "Stock Picking Validate",
    "version": "12.0.1.0.0",
    "category": "Personalized",
    "website": "https://odoo-community.org/",
    "author": "Esther Cisneros, Gebesa",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "stock",
    ],
    "data": [
        "data/ir_cron_data.xml",
        "security/security.xml",
        "views/stock_picking.xml",
        "wizard/product_replenish_views.xml",
        "wizard/stock_picking_make_batch_views.xml",
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
