# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Product Price List Multicompany",
    "summary": "Price List Multicompany",
    "version": "12.0.1.0.0",
    "category": "Products",
    "website": "https://odoo-community.org/",
    "author": "Daniel Gurrola, Gebesa",
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
        "sale",
        "res_company_manufacturer"
    ],
    "data": [
        "data/ir_cron.xml",
        "views/product_pricelist.xml",
        "views/sale_order.xml",
        "views/res_partner_view.xml",
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
