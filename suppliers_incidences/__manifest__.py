# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Suppliers Incidences",
    "summary": "Module for recording incidents with suppliers.",
    "version": "12.0.1.0.0",
    "category": "Purchases",
    "website": "https://odoo-community.org/",
    "author": "Deysy Mascorro, Gebesa",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "base",
        "purchase",
    ],
    "data": [
        'security/ir.model.access.csv',
        'views/supplier_incident_view.xml',
        'views/incident_secuence.xml'

    ],
    "demo": [

    ],
    "qweb": [

    ]
}
