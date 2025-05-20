# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "GEBESA integration cost",
    "summary": "Gebesa integration cost",
    "version": "12.0.1.0.0",
    "category": "Sale",
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
        "account",
        "account_analytic_everywhere",
        "stock_landed_costs",
        "system_administrator",
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/account_invoice.xml",
        "views/account_journal.xml",
        "views/integration_cost_gebesa.xml",
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
