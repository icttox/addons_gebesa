# -*- coding: utf-8 -*-
# © 2017 Aldo Nerio
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Maintenance GEBESA",
    "summary": "Maintenance GEBESA",
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
        "base",
        "maintenance",
    ],
    "data": [
        'security/maintenance_security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/maintenance_equipment_view.xml',
        'views/maintenance_request_view.xml',
        'reports/orden_servicio_mto.xml',
        'reports/orden_servicio_preventivo_mto.xml'
    ],
    "demo": [
    ],
    "qweb": [
    ],
    "post_init_hook": "post_init_hook",
}
