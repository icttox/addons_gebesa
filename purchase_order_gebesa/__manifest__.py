# -*- coding: utf-8 -*-
# © 2018 Aldo Nerio
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Purchase Order Gebesa",
    "summary": "Purchase Order Gebesa",
    "version": "12.0.1.0.0",
    "category": "Purchase",
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
        "product",
        'purchase_stock',
    ],
    "data": [
        "views/product_template_view.xml",
        "views/product_supplierinfo_view.xml",
        "data/ir_cron.xml",
        "reports/purchase_order_report.xml",
        "data/mail_template_data.xml",
        "views/purchase_ordes_view.xml",
    ],
    "demo": [

    ],
    "qweb": [

    ]
}
