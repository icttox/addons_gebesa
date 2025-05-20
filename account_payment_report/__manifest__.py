# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Payment report",
    "summary": "Report for payments",
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
        "base",
        "account",
        "l10n_mx_edi_extended",
    ],
    "data": [
        "report/report_payment.xml",
        "views/pivot_account_payment.xml"
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
