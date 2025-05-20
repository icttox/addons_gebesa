# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Product Document",
    "summary": "Product Document",
    "version": "12.0.1.0.0",
    "category": "MPR",
    "website": "https://odoo-community.org/",
    "author": "Armando Robledo, Gebesa",
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
        "integration_progress_fields",
        "product_structure_gebesa",
    ],
    "data": [
        "security/security.xml",
        "views/product_document_view.xml",
        "security/ir.model.access.csv",
        "views/document_product_view.xml"
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
