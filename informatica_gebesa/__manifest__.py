# -*- coding: utf-8 -*-
# © 2017 Aldo Nerio
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Informatica Gebesa",
    "summary": "Informatica Gebesa",
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
        "views/equipment_sequence.xml",
        "views/maintenance_equipment.xml",
        "views/maintenance_request.xml",
        "views/res_physical_location_view.xml",
        "reports/equipment_inventory.xml",
        "reports/order_servicio.xml",
        "security/ir.model.access.csv",
        "wizard/maintenance_equipment_employee_log_wz.xml",
        "views/it_software_view.xml",
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
