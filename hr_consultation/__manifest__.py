# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Consultation",
    "summary": "Hr Consultation",
    "version": "12.0.1.0.0",
    "category": "",
    "website": "https://odoo-community.org/",
    "author": "Leslie Marquez, Gebesa",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "base",
        "hr",
        "global_chatter"
    ],
    "data": [
        "views/hr_consultation_secuence.xml",
        "security/ir.model.access.csv",
        "views/hr_consultation_view.xml",
        "views/hr_consultation_prescription_view.xml",
        "views/hr_employee_view.xml",
    ],
    "demo": [

    ],
    "qweb": [

    ]
}
