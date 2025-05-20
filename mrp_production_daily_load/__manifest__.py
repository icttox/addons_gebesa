# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Production Daily Load",
    "summary": "Production Daily Load",
    "version": "12.0.1.0.0",
    "category": "MRP",
    "website": "https://odoo-community.org/",
    "author": " Leslie Marquez, Gebesa",
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
        "mrp_segment",

    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/mrp_production_daily_load_view.xml",
        "views/mrp_workcenter_view.xml",
        "views/mrp_operation_view.xml",
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
