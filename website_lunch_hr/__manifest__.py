# Copyright 2022, Cesar Barron
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "Comedor Gebesa",
    "summary": "Software auxiliar para comedor empresarial.",
    "version": "12.0.1.0.0",
    "category": "",
    "website": "https://odoo-community.org/",
    "author": "Cesar Barron, Gebesa",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "hr",
        "lunch",
        "website",
        "hr_salary_assignments"
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/data.xml",
        "data/ir_cron_data.xml",
        "views/assets.xml",
        "views/hr_employee_views.xml",
        "views/lunch_order_views.xml",
        "views/templates.xml",
        "reports/lunch_ticket.xml",
        "reports/employee_luch_password.xml",
        'reports/pvc_credential.xml',
    ],
    "demo": [

    ],
    "qweb": [

    ]
}
