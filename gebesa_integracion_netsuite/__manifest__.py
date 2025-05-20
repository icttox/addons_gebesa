# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Integration Netsuite",
    "summary": "Integration with Netsuite",
    "version": "12.0.1.0.0",
    "category": "Uncategorized",
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
        "stock",
        "product",
        "integration_netsuite_fields",
    ],
    "data": [
        "views/account_invoice_view.xml",
        "data/product_nst_plant.xml",
        "data/product_nst_line.xml",
        "data/product_nst_tipo.xml",
        "wizard/product_send_netsuite.xml",
        "views/product_product.xml",
        "security/ir.model.access.csv",
        "security/security.xml",
    ],
    "demo": [

    ],
    "qweb": [

    ]
}
