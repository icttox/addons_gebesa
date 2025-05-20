# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Report Price List",
    "summary": "Report Price List",
    "version": "Product",
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
        "product_structure_gebesa",
        "report_qweb_element_page_visibility",
        "product_variant_default_code",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/report_paperformat.xml",
        "views/product_template.xml",
        "views/product_product_view.xml",
        "views/product_pricelist_category_view.xml",
        "report/report_price_layout.xml",
        "report/report_price_list.xml",
        "report/report_price.xml",
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
