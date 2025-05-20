# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Mrp Production procure",
    "summary": "This is for lazy production managers",
    "version": "12.0.1.0.0",
    "category": "Mrp",
    "website": "https://odoo-community.org/",
    "author": "Cesar Barron, Gebesa",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "base", "mrp", "stock", "stock_warehouse_analytic_id"
    ],
    "data": [
        "wizards/mrp_production_procure.xml",
    ],
    "demo": [
        "demo/res_partner_demo.xml",
    ],
    "qweb": [
        "static/src/xml/module_name.xml",
    ]
}
