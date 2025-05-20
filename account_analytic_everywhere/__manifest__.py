# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Account Analytic Everywhere",
    "summary": "Add field analytic_account",
    "version": "12.0.1.0.0",
    "category": "Accounting",
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
        "base", "account", "stock",
        "purchase", "mrp", "sale_order_gebesa",
        "sale", 'purchase_stock',
        "account_invoice_purchase_order_data",
        "res_company_manufacturer",
        "product_structure_gebesa",
    ],
    "data": [
        "views/account_invoice.xml",
        "views/purchase_order.xml",
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
