# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Reports Wizard Segment",
    "summary": "Reports Wizard Segment",
    "version": "11.0.1.0.0",
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
        "mrp_segment",
        "product",
        "gebesa_reports",
    ],
    "data": [
        "wizard/export_segment_armed.xml",
        "wizard/export_mp_concentrado.xml",
        "wizard/export_order_wood.xml"
    ],
    "demo": [

    ],
    "qweb": [

    ]
}
