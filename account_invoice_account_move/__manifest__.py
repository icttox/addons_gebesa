# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Account invoice - Account move",
    "summary": "Account invoice - Account move",
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
        "base", "account",
        "account_invoice_sale_data", "res_settings_freight",
        "account_invoice_rate",
        # "system_administrator",
        "stock_landed_costs",
    ],
    "data": [
        "views/account_invoice.xml",
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
