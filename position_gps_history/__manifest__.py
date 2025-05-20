# -*- coding: utf-8 -*-
# © <2017> <Samuel Barron>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Position GPS History",
    "summary": "Position GPS History",
    "version": "12.0.1.0.0",
    "category": "Transport",
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
        "base",
        "fleet",
        "flete_gebesa",
        "tms",
    ],
    "data": [
        "views/position_gps_history.xml",
        "views/fleet_vehicle.xml",
        "security/ir.model.access.csv"
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
