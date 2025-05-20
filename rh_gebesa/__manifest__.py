# -*- coding: utf-8 -*-
# © 2018 Aldo Nerio
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "RH Gebesa",
    "summary": "RH Gebesa",
    "version": "11.0.1.0.0",
    "category": "Personalized",
    "website": "https://odoo-community.org/",
    "author": "Aldo Nerio, Gebesa",
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
        "hr_contract",
        "hr_holidays",
    ],
    "data": [
        "security/security.xml",
        "data/employee_sequence.xml",
        "data/hr_leave_type.xml",
        "views/hr_department.xml",
        "views/hr_employee.xml",
        "views/hr_job_view.xml",
        "views/hr_contract.xml",
        "views/hr_leave.xml",
        "views/hr_leave_type.xml",
        "views/resource_calendar.xml",
        "views/webclient_templates.xml",
        "reports/ingreso_personal.xml",
        "reports/contrato_tiempo_indeterminado.xml",
        "reports/contrato_tiempo_determinado.xml",
        "reports/contrato_admonlag_indeterminado.xml",
        "reports/contrato_admonlag_determinado.xml",
        "reports/contrato.xml",
        "reports/orden_movimiento_personal.xml",
        "reports/contrato_admonlag.xml",
        "wizard/employee_consecutive_forchange.xml",
        "wizard/employee_company_change_wizard.xml",
        "data/ir_cron.xml",
    ],
    "demo": [
    ],
    "qweb": [
        "static/src/xml/menu_vacaciones.xml",
    ]
}
