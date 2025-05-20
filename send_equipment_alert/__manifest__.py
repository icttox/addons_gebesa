# -*- coding: utf-8 -*-
# © 2017 Aldo Nerio
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Alerta de Equipo Gebesa",
    "summary": "Alerta de Equipo Gebesa",
    "version": "12.0.1.0.0",
    "category": "Personalized",
    "website": "https://odoo-community.org/",
    "author": "Daniel Gurrola, Gebesa",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "base",
        "maintenance",
    ],
    "data": [
        "views/send_equipment_alert.xml",
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
