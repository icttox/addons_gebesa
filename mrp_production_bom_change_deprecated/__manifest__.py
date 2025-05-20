# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Mrp production bom change",
    "summary": "Mrp production bom change",
    "version": "12.0.1.0.0",
    "category": "MRP",
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
        "mrp",
        "mrp_plm",
        # "system_administrator",
    ],
    "data": [
        'views/mrp_bom.xml',
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
