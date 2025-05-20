# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Payroll import",
    "summary": "Payroll import",
    "version": "12.0.1.0.0",
    "category": "Accounting",
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
        "base", "account", "hr_payroll"
    ],
    "data": [
        "security/payroll_import_security.xml",
        "views/payroll_import.xml",
        "wizards/payroll_import_microsip.xml",
        "views/res_company.xml",
        "security/ir.model.access.csv",
        "views/hr_payslip_view.xml",
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
