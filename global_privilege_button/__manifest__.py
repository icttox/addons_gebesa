# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Global Privilege Button",
    "summary": "Creates a security group that limits the visibility of button",
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
        "product",
        "purchase",
        "mrp_cut_detail",
    ],
    "data": [
        "security/security.xml",
        "views/product_template_view.xml",
        "views/purchase_order_view.xml",
        "views/account_invoice_view.xml",
        "views/mrp_bom_view.xml",
        "views/stock_move.xml",
    ],
    "demo": [

    ],
    "qweb": [

    ]
}
