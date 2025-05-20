# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Evidence Payment Validate",
    "summary": "Evidence Payment Validate",
    "version": "12.0.1.0.0",
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
        "account",
        "account_invoice_sale_data",

    ],
    "data": [
        "security/security.xml",
        "views/account_invoice_view.xml",
        "views/res_partner_view.xml",
        "wizards/account_invoice_wizard_evi.xml",

    ],
    "demo": [

    ],
    "qweb": [

    ]
}
