# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Sale order GEBESA",
    "summary": "sale order GEBESA",
    "version": "12.0.1.0.0",
    "category": "Personalizado",
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
        "base", "sale", "stock",
        "project",
        "stock_warehouse_analytic_id",
        "product_product_data_validator",
        "product",
        "sale_stock",
        "sale_margin",
        "res_partner_suspendit_credit",
        "delivery"
    ],
    "data": [
        "security/security.xml",
        "views/sale_order.xml",
        "views/account_analytic_account_view.xml",
        "views/res_partner_view.xml",
        "views/product_product_sale.xml",
        "report/sale_report_template.xml",
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
