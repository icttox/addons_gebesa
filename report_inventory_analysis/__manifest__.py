# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Report Inventory analysis",
    "summary": "Report Inventory analysis",
    "version": "12.0.1.0.0",
    "category": "Warehouse",
    "website": "https://odoo-community.org/",
    "author": "Samuel Barron, Eduardo Lopez ,Gebesa",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "base",
        "stock",
        "product_structure_gebesa",
    ],
    "data": [
        "wizards/report_inventory_analysis.xml"
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
