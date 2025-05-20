# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Report Shipment Instruction",
    "summary": "Invoice Report",
    "version": "12.0.1.0.0",
    "category": "Account",
    "website": "https://odoo-community.org/",
    "author": "Armando Robledo, Gebesa",
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
        'sale_order_gebesa',
        # 'website_quote',
        'mail',
        'mrp',
        'mrp_shipment',
        'report_tags',
    ],
    "data": [
        "report/shipment_instruction_report_view.xml",
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
