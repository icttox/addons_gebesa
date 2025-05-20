# -*- coding: utf-8 -*-
# © <2017> <Aldo Nerio>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Website Cut Detail",
    "summary": "Website Cut Detail",
    "version": "12.0.1.0.0",
    "category": "Uncategorized",
    "website": "https://odoo-community.org/",
    "author": "Aldo Nerio, Gebesa",
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
        "mrp_cut_detail",
    ],
    "data": [
        "wizards/wizard_cut_detail.xml",
        "views/mrp_bom.xml"
    ],
    "demo": [

    ],
    "qweb": [

    ]
}
