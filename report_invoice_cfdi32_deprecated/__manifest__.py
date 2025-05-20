# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Report Invoice CFD-I 32",
    "summary": "Invoice Report",
    "version": "11.0.1.0.0",
    "category": "Account",
    "website": "https://odoo-community.org/",
    "author": "Samuel Barron, Gebesa",
    "license": "AGPL-3",
    "application": False,
    "installable": False,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "base",
        "cfdi32",
    ],
    "data": [
        "report/invoice_cfdi_report.xml",
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
