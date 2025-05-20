# -*- coding: utf-8 -*-
# © <2017> <Aldo Nerio>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Sale Order Check Exceptions",
    "summary": "Sale Order Check Exceptions",
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
        "sale",
        "stock",
        "mrp_segment",
        "product_product_data_validator",
        "stock_move_batch_validator"
        # "sale_order_ok_etl",
    ],
    "data": [
        "security/security.xml",
        # "views/sale_order.xml",
        "wizards/sale_order_check_exceptions_wizard.xml",
    ],
    "demo": [

    ],
    "qweb": [

    ]
}
