# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Product structure gebesa",
    "summary": "Product structure gebesa",
    "version": "12.0.1.0.0",
    "category": "Product",
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
        "stock",
        "purchase",
        "purchase_stock",
        "product_variant_default_code",
        "product_multi_company",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "views/product_family.xml",
        "views/product_group.xml",
        "views/product_line.xml",
        "views/product_type.xml",
        "views/product_template.xml",
        "views/product_product.xml",
        "views/product_tree.xml",
        "views/product_kanban.xml",
        "views/product_kanban_view.xml",
        "wizards/product_family_update_wizard.xml",
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
