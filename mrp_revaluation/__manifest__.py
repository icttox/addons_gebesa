# -*- coding: utf-8 -*-
# © <2016> <César Barrón>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "MRP Revaluation",
    "summary": "Performs a recursive revaluation, when a product"
    " is in a BOM and its standar_price changes, it applies the "
    "changes to all the products tha has it in his BOM",
    "version": "12.0.1.0.0",
    "category": "Stock Account",
    "website": "https://odoo-community.org/",
    "author": "Cesar Barron, Gebesa",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "base", "stock", "account", "stock_account",
        "mrp",
        "product_structure_gebesa",
    ],
    "data": [
        "security/mrp_revaluation_security.xml",
        "security/ir.model.access.csv",
        "views/mrp_bom_view.xml",
        "views/stock_revaluation_view.xml",
        "views/product_product_view.xml",
        "views/stock_config_settings.xml",
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
