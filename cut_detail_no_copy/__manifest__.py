# -*- coding: utf-8 -*-
# © <2018> <Aldo Nerio>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Cut Detail No Copy",
    "summary": "Cut Detail No Copy",
    "version": "12.0.1.0.0",
    "category": "MRP",
    "website": "https://odoo-community.org/",
    "author": "Aldo Nerio, Gebesa",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "base",
        "mrp",
        "mrp_cut_detail",
    ],
    "data": [
        "security/security.xml",
        "views/mrp_bom.xml"
    ],
    "demo": [

    ],
    "qweb": [

    ]
}
