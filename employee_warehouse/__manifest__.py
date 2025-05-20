# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Warehouse in employee",
    "summary": "Warehouse in employee",
    "version": "12.0.1.0.0",
    "category": "Human Resources",
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
        "base", "hr", "stock",
        "stock_inventory_negative_line",
        "mrp"
    ],
    "data": [
        "views/hr_employee.xml",
        "views/stock_inventory.xml",
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
