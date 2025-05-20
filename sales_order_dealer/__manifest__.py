# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Sale Order Dealer.",
    "summary": "Sale Order Dealer.",
    "version": "12.0.3.7",
    "category": "Uncategorized",
    "website": "https://odoo-community.org/",
    "author": "Esther Cisneros, Gebesa",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "base",
        "sale",
        "mrp",
        "account_invoice_sale_data",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/res_partner_dealer_view.xml",
        'views/sale_order.xml',
        'views/mrp_production.xml',
        'views/res_partner.xml',
    ],
    "demo": [

    ],
    "qweb": [

    ]
}
