# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Report Js sale",
    "summary": "Report Js sale",
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
        'base',
        'sale',
        "week_number_validate",
    ],
    "data": [
        # "reports/sale_order_js_report.xml",
    ],
    "demo": [
    ],
    "qweb": [
        # "static/src/xml/sale_report_js_backend.xml",
    ]
}
