# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Global Product View",
    "summary": "Change to Product Views.",
    "version": "12.0.1.0.0",
    "category": "Generic Modules",
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
        "stock",
        "integration_netsuite_fields",
        "integration_progress_fields",
        "catalogs_cfdi",
        "product_structure_gebesa",
        "product_variant_default_code",
        "stock_landed_costs",
    ],
    "data": [
        "views/product_template_view.xml",
        "views/product_product_view.xml",
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
