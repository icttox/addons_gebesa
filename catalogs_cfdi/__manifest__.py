# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Catalog CFDI",
    "summary": "Catalogo para el CFDI",
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
        "account",
        "product",
        "stock",
        "mx_locations",
        "foreign_commerce_complement",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/catalog_product_service_view.xml",
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
