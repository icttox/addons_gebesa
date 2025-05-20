# -*- coding: utf-8 -*-
# © 2017 Aldo Nerio
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Detalles Dinamicos",
    "summary": "Detalles Dinamicos",
    "version": "12.0.1.0.0",
    "category": "MRP",
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
        "product",
        "stock",
        "mrp",
        "mrp_cut_detail",
        "cut_detail_no_copy",
    ],
    "data": [
        "security/security.xml",
        "security/bom_selective_replace_security.xml",
        "security/mrp_bom_product_replacement.xml",
        "security/ir.model.access.csv",
        "wizards/product_replacement_import_views.xml",
        "views/mrp_bom_line.xml",
        "views/mrp_bom.xml",
        "views/mrp_bom_product_replacement.xml",
        "views/product_attribute_value_equivalent.xml",
        "views/bom_selective_replace.xml",
        "views/mrp_import_product_replacement.xml",
        "data/ir_cron_data.xml",
    ],
    "demo": [

    ],
    "qweb": [

    ]
}
